"""Orange Canvas Widget for the CTA's module. It is the main result of the workflow.
Helps to claim facts about the corpus from upstream evidences."""

from typing import Any, Optional

import numpy as np
from Orange.data import ContinuousVariable, Domain, StringVariable, Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Input, Output

from cta_orange.helpers.ref import CTARef
from cta_orange.helpers.session import CTASession
from cta_orange.helpers.widgets import OWCTAKernelBase
from cta_orange.helpers.orange_datatable import create_orange_datatable


def _single_line(text: str) -> str:
    """Render a potentially multi-line string into a compact single line."""
    return " ".join(str(text).splitlines()).strip()


class OrangeCTAClaim(OWCTAKernelBase):
    """The class for creating the claim widget"""

    name = "Claim"

    description = "Lets the user make a scientific claim on an text corpus."

    icon = "icons/claim.png"

    priority = 10

    class Inputs:
        """Inputs definition of the widget"""

        scalar_a = Input("CTA Data A", (CTASession, CTARef), auto_summary=False)
        scalar_b = Input("CTA Data B", (CTASession, CTARef), auto_summary=False)

    class Outputs:
        """Outputs definition of the widget"""

        cta_data = Output("CTA Data", (CTASession, CTARef), auto_summary=False)
        data_table = Output("Data Table", Table)

    op_id = "Claim"
    out_port = "claim"

    mode = Setting("Compare")
    theta = Setting(0.5)
    delta = Setting(0.3)
    want_main_area = False
    resizing_enabled = True

    def __init__(self):
        """Manages the class creation. Basic UI is created here."""
        super().__init__()
        self.scalar_a = None
        self.scalar_b = None
        basicBox = gui.widgetBox(
            widget=self.controlArea,
            box="Options",
            orientation="vertical",
        )
        basicBoxLine1 = gui.widgetBox(
            widget=basicBox,
            box=False,
            orientation="horizontal",
        )
        gui.comboBox(
            widget=basicBoxLine1,
            master=self,
            orientation="horizontal",
            value="mode",
            items=["Compare", "Threshold"],
            label="Mode :",
            callback=self.changeMode,
            tooltip=("Compare two scalars, or check one against a fixed threshold."),
            labelWidth=100,
            sendSelectedValue=True,
        )
        self.delimiterLineTheta = gui.widgetBox(
            widget=basicBox,
            box=False,
            orientation="horizontal",
        )
        gui.lineEdit(
            widget=self.delimiterLineTheta,
            master=self,
            value="theta",
            orientation="horizontal",
            label="θ:",
            labelWidth=100,
            # callback=self.sendButton.settingsChanged,
            tooltip=("θ: the threshold value the scalar must exceed (Threshold mode)."),
            valueType=float,
            # validator=QDoubleValidator(),
        )
        self.delimiterLineDelta = gui.widgetBox(
            widget=basicBox,
            box=False,
            orientation="horizontal",
        )
        gui.lineEdit(
            widget=self.delimiterLineDelta,
            master=self,
            value="delta",
            orientation="horizontal",
            label="δ_0:",
            labelWidth=100,
            # callback=self.sendButton.settingsChanged,
            tooltip=("δ₀: the minimum margin required between the two scalars (Compare mode)."),
            valueType=float,
        )
        basicBox2 = gui.widgetBox(
            widget=self.controlArea,
            box="Computed result",
            orientation="vertical",
        )

        # Compact, single-line outputs (better for screenshots).
        self.status_text = ""
        self.reasons_text = ""
        self.missing_text = ""
        self.mismatch_text = ""

        self.statusLineEdit = gui.lineEdit(
            widget=basicBox2,
            master=self,
            value="status_text",
            orientation="horizontal",
            label="Status:",
            labelWidth=100,
        )
        self.statusLineEdit.setReadOnly(True)
        self.statusLineEdit.setMaximumHeight(22)

        self.reasonsLineEdit = gui.lineEdit(
            widget=basicBox2,
            master=self,
            value="reasons_text",
            orientation="horizontal",
            label="Reason:",
            labelWidth=100,
        )
        self.reasonsLineEdit.setReadOnly(True)
        self.reasonsLineEdit.setMaximumHeight(22)

        self.missingLineEdit = gui.lineEdit(
            widget=basicBox2,
            master=self,
            value="missing_text",
            orientation="horizontal",
            label="Missing inputs:",
            labelWidth=100,
        )
        self.missingLineEdit.setReadOnly(True)
        self.missingLineEdit.setMaximumHeight(22)

        self.mismatchLineEdit = gui.lineEdit(
            widget=basicBox2,
            master=self,
            value="mismatch_text",
            orientation="horizontal",
            label="Mismatches:",
            labelWidth=100,
        )
        self.mismatchLineEdit.setReadOnly(True)
        self.mismatchLineEdit.setMaximumHeight(22)

        basicBox3 = gui.widgetBox(
            widget=self.controlArea,
            box="Sensitivity check",
            orientation="vertical",
        )
        gui.button(
            widget=basicBox3,
            master=self,
            label="Run source-weighting policy check",
            callback=self.robustnessSweep,
            tooltip=("Run a robustness sweep across source-weighting policies and display the result as a table."),
        )
        # gui.rubber(self.controlArea)
        gui.button(
            widget=self.controlArea,
            master=self,
            label="Send",
            callback=self.sendData,
            tooltip=("Send the data to process it."),
        )
        self.delimiterLineTheta.setVisible(False)
        # Fix the widget's height to the minimum
        self.setMaximumHeight(self.minimumSizeHint().height())

    @Inputs.scalar_a
    def set_scalar_a(self, scalar_a: Optional[tuple]) -> None:
        """
        Receive the upstream CTAData : the session and a ref to the upstream proportion
        Session is set here
        """
        # Store the new ref and trigger recomputation if possible.
        session, ref = scalar_a if scalar_a is not None else (None, None)
        self._logic.session = session
        self.scalar_a = ref

    @Inputs.scalar_b
    def set_scalar_b(self, scalar_b: Optional[tuple]) -> None:
        """
        Receive the upstream CTAData : the session and a ref to the upstream proportion
        Session is *NOT* set here. Gets only the proportion.
        """
        # Store the new ref and trigger recomputation if possible.
        self.scalar_b = scalar_b[1] if scalar_b is not None else None

    def _params(self) -> dict[str, Any]:
        """
        Collect widget parameters for the operator call.

        Returns:
            dict[str, Any]: The parameters recorded onto the GraphSpec.
        """
        # Parameters are recorded into the GraphSpec and influence caching.
        low_mode =self.mode.lower()
        params = {"mode": low_mode}
        if low_mode == "threshold":
            params["theta"] = float(self.theta)
        elif low_mode == "compare":
            params["delta0"] = float(self.delta)

        return params

    def _params_sweep(self) -> dict[str, Any]:
        """
        Collect widget parameters for the sweep call.

        Returns:
            dict[str, Any]: The parameters recorded onto the GraphSpec.
        """
        # Parameters are recorded into the GraphSpec and influence caching.
        params = {"K": 2, "delta0": float(self.delta)}
        return params

    def _collect_inputs(self) -> dict[str, Optional[CTARef]]:
        """
        Collect wiring inputs for the operator call.
        Also clears any leftover from a previous sweep run

        Returns:
            dict[str, Optional[CTARef]]: the ref to the proportions received upstream.
        """
        self._logic.session.registry.clear_input(self._logic.node_id, "string_store")
        return {
            "scalar_A": self.scalar_a,
            "scalar_B": self.scalar_b if self.scalar_b else None,
        }

    def _collect_inputs_sweep(self) -> dict[str, Optional[CTARef]]:
        """
        Collect wiring inputs for the sweep call.

        Returns:
            dict[str, Optional[CTARef]]: the ref to the evidences used for the sweep
        """
        list_evidences= self._logic.session.all_evidence()
        ev_str_store = None
        for ev in list_evidences:
            if ev.type_id == "StringStore":
                ev_str_store = CTARef.from_evidence(
                    session_id=self._logic.session.session_id,
                    node_id=ev.prov.origin_node_id,
                    port="string_store",
                    evidence=ev,
                )
        return {
            "string_store": ev_str_store,
            "scalar_A": self.scalar_a,
            "scalar_B": self.scalar_b if self.scalar_b else None,
        }

    def _send_none(self) -> None:
        """Clear outputs of the claim widget"""
        self.Outputs.cta_data.send((None, None))
        self.Outputs.data_table.send(None)

    def _send_ref(self, ref):
        """
        Sends the session and the ref to output or sends an orange data_table for the sweep

        Args:
            ref (CTARef): the reference to the evidence to send.

        Returns:
            CTARef: The same reference to the evidence to send to be able to chain on it.
        """
        ev = self._logic.session.evidence(ref)
        if ev.type_id == "Table":
            ev = self._logic.session.evidence(ref)
            payload = ev.payload
            if payload["meta"]["K"] == 2:
                columns = [
                    c
                    for c in payload["columns"]
                    if c not in ["alpha_cap", "alpha_mult"]
                ]
            else:
                columns = payload["columns"][:]
            data_table = create_orange_datatable(payload["rows"], columns)
            self.Outputs.data_table.send(data_table)
        else:
            self.Outputs.cta_data.send((self._logic.session, ref))
            # Clear (compact) UI fields.
            self.clearLines()
            if ev.payload:
                reasons_full = "\n".join(ev.payload.get("reasons") or [])
                reasons_line = _single_line(reasons_full)
                self.reasonsLineEdit.setText(reasons_line)
                self.reasonsLineEdit.setToolTip(reasons_full)
                str_missing = ""
                if ev.payload["missing_scope_fields"]:
                    str_missing += (
                        "Missing scope fields:\n"
                        + "-" * 40
                        + "\n".join(ev.payload["missing_scope_fields"])
                    )
                if ev.payload["missing_evidence_refs"]:
                    if str_missing:
                        str_missing += "\n"
                    str_missing += (
                        "Missing evidence references"
                        + "-" * 40
                        + "\n".join(ev.payload["missing_evidence_refs"])
                    )

                missing_full = str_missing
                missing_line = _single_line(missing_full)
                self.missingLineEdit.setText(missing_line)
                self.missingLineEdit.setToolTip(missing_full)

                mismatch_full = "\n".join(ev.payload.get("compatibility_mismatches") or [])
                mismatch_line = _single_line(mismatch_full)
                self.mismatchLineEdit.setText(mismatch_line)
                self.mismatchLineEdit.setToolTip(mismatch_full)

                status_full = str(ev.payload.get("status", ""))
                status_line = _single_line(status_full)
                self.statusLineEdit.setText(status_line)
                self.statusLineEdit.setToolTip(status_full)

                # Make sure the beginning of each field is visible (useful for screenshots).
                for w in (
                    self.statusLineEdit,
                    self.reasonsLineEdit,
                    self.missingLineEdit,
                    self.mismatchLineEdit,
                ):
                    try:
                        w.setCursorPosition(0)
                    except Exception:
                        pass
        return ref

    def sendData(self):
        """Manual trigger for the Send button."""
        self.handleNewSignals()

    def handleNewSignals(self):
        """
        Sends the data to Output. Here it means the CTASession object,
        as well as a CTARef to a claim.

        Returns:
            Optional[CTARef]: None if no upstream, the ref to evidence otherwise
        """
        self.error()
        self.information()
        self.clearLines()
        # Check the upstream is linked
        if self.scalar_a is None or self._logic.session is None:
            self.error("Upstream data(s) are not connected.")
            self._send_none()
            return None
        if self.scalar_b is None and self.mode == "Compare":
            self.information("Don't forget to provide another scalar.")
        ev_ref = super().handleNewSignals()
        return ev_ref

    def changeMode(self):
        """Show or hide the delimiter field depending on the selected mode."""
        if self.mode == "Threshold":
            self.delimiterLineTheta.setVisible(True)
            self.delimiterLineDelta.setVisible(False)
        elif self.mode == "Compare":
            self.delimiterLineTheta.setVisible(False)
            self.delimiterLineDelta.setVisible(True)

    def clearLines(self):
        """Clear the widgets lines"""
        self.reasonsLineEdit.clear()
        self.statusLineEdit.clear()
        self.mismatchLineEdit.clear()
        self.missingLineEdit.clear()

    def robustnessSweep(self):
        """Makes a robustness sweep

        Returns:
            CTARef: a reference to the data table produced
        """
        sweep_node_id = self._logic.node_id + "_sweep"
        self.error()
        self.warning()
        if self.scalar_a is None or self.scalar_b is None or self._logic.session is None:
            self.error("Upstream data are not connected.")
            return None
        inputs = self._collect_inputs_sweep()
        # make the operation only when the button is clicked
        self._logic.session.registry.upsert_node(
            sweep_node_id,
            op_id="RobustnessSweepCapContinuum",
            params=self._params_sweep(),
        )
        # Mirror input edges into the registry (clear on None).
        for input_name, ref in inputs.items():
            if ref is None:
                self._logic.session.registry.clear_input(
                    self._logic.node_id, input_name
                )
            else:
                self._logic.session.registry.set_input(
                    self._logic.node_id, input_name, ref
                )
        # Execute the kernel for the closure needed to compute this node.
        try:
            self._logic.session.ensure_computed(self._logic.node_id)
        except Exception as exc:
            self.error(f"Sweep failed: {exc}")
            return None
        # Resolve the output evidence and emit a CTARef.
        out_ref = self._logic.session.output_ref(self._logic.node_id, port="table")
        return self._send_ref(out_ref)

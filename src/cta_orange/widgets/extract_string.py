"""Orange Canvas Widget for the CTA's module. Extract strings from
a table's column."""

from typing import Any

from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Input, Output

from cta_orange.helpers.orange_datatable import create_orange_datatable
from cta_orange.helpers.ref import CTARef
from cta_orange.helpers.session import CTASession
from cta_orange.helpers.widgets import OWCTAKernelBase


class ExtractStringsCTA(OWCTAKernelBase):
    """Widget that extracts distinct strings from a table column into a string store."""
    # Widget's name as displayed in the canvas
    name = "Extract Strings"
    # Short widget description
    description = "Extract strings from a table's column"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/extract_strings.png"
    priority = 10

    # Widget's outputs; here, a single output named "Number", of type int
    class Inputs:
        """Inputs definition of the widget"""

        cta_data = Input("CTA Data", (CTASession, CTARef), auto_summary=False)

    class Outputs:
        """Outputs definition of the widget"""

        cta_data = Output("CTA Data", (CTASession, CTARef), auto_summary=False)
        data_table = Output("Table", Table)

    op_id = "BuildStringStore"
    out_port = "string_store"


    string_col = Setting("")
    source_id_cols = Setting("")
    normalization_policy = Setting(0)

    want_main_area = False
    resizing_enabled = False

    def __init__(self):
        """Manages the class creation. Basic UI is created here."""
        super().__init__()
        self.kinds=["none", "strip", "lower", "nfkc", "emoji_strip_skin_tone"]
        self.ref: CTARef | None = None
        basicBox = gui.widgetBox(
            widget=self.controlArea,
            box="Importation's mode",
            orientation="vertical",
        )
        basicBoxLine1 = gui.widgetBox(
            widget=basicBox,
            box=False,
            orientation="horizontal",
        )
        gui.lineEdit(
            widget=basicBoxLine1,
            master=self,
            value="string_col",
            orientation="horizontal",
            label="Column name :",
            labelWidth=150,
            # callback=self.sendButton.settingsChanged,
            tooltip=("Name of the column to import."),
        )
        gui.separator(widget=basicBox, width=5)
        basicBoxLine2 = gui.widgetBox(
            widget=basicBox,
            box=False,
            orientation="horizontal",
        )
        gui.lineEdit(
            widget=basicBoxLine2,
            master=self,
            value="source_id_cols",
            orientation="horizontal",
            label="ID of sources columns :",
            # TODO : ==user
            labelWidth=150,
            # callback=self.sendButton.settingsChanged,
            tooltip=("Names of the sources columns."),
        )
        gui.separator(widget=basicBox, width=5)
        basicBoxLine3 = gui.widgetBox(
            widget=basicBox,
            box=False,
            orientation="horizontal",
        )
        gui.comboBox(
            widget=basicBoxLine3,
            master=self,
            value="normalization_policy",
            orientation="horizontal",
            label="Normalization policy :",
            labelWidth=150,
            items=self.kinds,
            # callback=self.sendButton.settingsChanged,
            tooltip=("The normalization policy to use."),
        )
        gui.separator(widget=self.controlArea, width=5)
        gui.rubber(self.controlArea)
        gui.button(
            widget=self.controlArea,
            master=self,
            label="Send",
            callback=self.sendData,
            tooltip=("Send the data to process it."),
        )
        # Fix the widget's height to the minimum
        self.setFixedHeight(self.minimumSizeHint().height())

    @Inputs.cta_data
    def set_ctaData(self, cta_data: tuple | None) -> None:
        """
        Receive the upstream CTAData : the session and a ref to the upstream raw_table
        """
        # Store the new ref and trigger recomputation if possible.
        session, ref = cta_data if cta_data is not None else (None,None)
        self._logic.session = session
        self.ref = ref

    def _params(self) -> dict[str, Any]:
        """
        Collect widget parameters for the operator call.

        Returns:
            Dict[str, Any]: The parameters recorded onto the GraphSpec.
        """
        sources_list = [x for x in self.source_id_cols.replace(" ", "").split(",") if x]
        # Parameters are recorded into the GraphSpec and influence caching.
        return {
            "string_col": self.string_col,
            "source_id_cols": sources_list,
            "normalization_policy": {"kind": self.kinds[self.normalization_policy]}
        }

    def _collect_inputs(self) -> dict[str, CTARef | None]:
        """
        Collect wiring inputs for the operator call.

        Returns:
            Dict[str, Optional[CTARef]]: the raw table received from LoadTSV
        """
        return {"raw_table": self.ref}

    def _send_none(self) -> None:
        """Clear outputs of the widget"""
        self.Outputs.cta_data.send((None, None))
        self.Outputs.data_table.send(None)

    def _send_ref(self, ref):
        """
        Sends the session and the ref to output.

        Args:
            ref (CTARef): Reference to the evidence to send

        Returns:
            CTARef: The same reference to the evidence to send to be able to chain on it.
        """
        self.Outputs.cta_data.send((self._logic.session, ref))
        return ref

    def sendData(self):
        """Manual trigger for the Send button."""
        self.handleNewSignals()

    def handleNewSignals(self):
        """
        Sends the data to Output. Here it means the CTASession object,
        as well as a CTARef to a strings store created and an orange data_table

        Returns:
            Optional[bool]: None if no upstream or falsely named columns, True otherwise
        """
        self.error()
        if self.ref is None or self._logic.session is None:
            self.error("No upstream data connected.")
            self._send_none()
            return None
        upstream_ev = self._logic.session.evidence(self.ref)
        upstream_columns = upstream_ev.payload.get("columns") if upstream_ev else None

        sources_list = [x for x in self.source_id_cols.replace(" ", "").split(",") if x]

        if upstream_columns is not None:
            missing = [c for c in [self.string_col, *sources_list] if c not in upstream_columns]
            if missing:
                self.error(f"Column(s) not found in upstream table: {', '.join(missing)}")
                self._send_none()
                return None

        ev_ref = super().handleNewSignals()
        if ev_ref:
            ev = self._logic.session.evidence(ev_ref)
            # Récupération de la raw_table puis transformation en Table d'Orange
            payload = ev.payload
            if payload:
                data_table = create_orange_datatable(payload["strings"], ["string_id", "string", "count"])
                self.Outputs.data_table.send(data_table)
                return True
        self.Outputs.data_table.send(None)
        return True

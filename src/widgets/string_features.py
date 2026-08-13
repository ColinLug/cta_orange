"""
Orange Canvas Widget for the CTA's module.

Creates a Data Table of the imported segmented corpus strings.
"""

from typing import Any, Optional

import numpy as np
from AnyQt.QtGui import QIntValidator
from Orange.data import ContinuousVariable, Domain, StringVariable, Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Input, Output

from cta_orange.helpers.ref import CTARef
from cta_orange.helpers.session import CTASession
from cta_orange.helpers.widgets import OWCTAKernelBase


class CTAStringsFeatures(OWCTAKernelBase):
    """Creates a Data Table of the imported segmented corpus strings."""
    # Widget's name as displayed in the canvas
    name = "Strings Features"
    # Short widget description
    description = "Creates a Data Table of the imported segmented corpus strings."

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/strings_features.png"

    priority = 10

    # Widget's outputs; here, a single output named "Number", of type int
    class Inputs:
        """Inputs definition of the widget"""

        cta_data = Input("CTA Data", (CTASession, CTARef), auto_summary=False)

    class Outputs:
        """Outputs definition of the widget"""

        cta_data = Output("CTA Data", (CTASession, CTARef), auto_summary=False)
        data_table = Output("Table", Table)

    op_id = "StringFeatures"
    out_port = "table"

    top_k = Setting(20)
    want_main_area = False
    resizing_enabled = False

    def __init__(self):
        """Manages the class creation. Basic UI is created here."""
        super().__init__()
        self.ref: Optional[CTARef] = None
        basicBox = gui.widgetBox(
            widget=self.controlArea,
            box="Features",
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
            value="top_k",
            orientation="horizontal",
            label="Top k :",
            labelWidth=150,
            # callback=self.sendButton.settingsChanged,
            tooltip=("The number of top (most frequent) strings to keep."),
            valueType=int,
            validator=QIntValidator(1,9999999),
        )
        sendButton = gui.button(
            widget=self.controlArea,
            master=self,
            label="Send",
            callback=self.sendData,
            tooltip=("Send the data to process it."),
        )

    @Inputs.cta_data
    def set_ctaData(self, cta_data: Optional[tuple]) -> None:  # noqa: D401
        """Receive the upstream CTAData : the session and a ref to the upstream segmentation"""

        # Store the new ref and trigger recomputation if possible.
        session, ref = cta_data if cta_data is not None else (None,None)
        self._logic.session = session
        self.ref = ref

    def _params(self) -> dict[str, Any]:
        """
        Collect widget parameters for the operator call.

        Returns:
            dict[str, Any]: The parameters recorded onto the GraphSpec.
        """
        # Parameters are recorded into the GraphSpec and influence caching.
        return {"top_k": self.top_k}

    def _collect_inputs(self) -> dict[str, Optional[CTARef]]:
        """
        Collect wiring inputs for the operator call.

        Returns:
            dict[str, Optional[CTARef]]: the ref to the segmentation received from CTASegmentation
        """
        return {"strings": self.ref}

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
        as well as a CTARef to a segmentation and an orange data_table.

        Returns:
            Optional[bool]: None if no upstream or invalid top_k, True otherwise
        """
        self.error()
        self.warning()
        if self.ref is None or self._logic.session is None:
            self.error("No upstream data connected.")
            self._send_none()
            return None
        if self.top_k is None or self.top_k < 1:
            self.error("Top k must be a positive integer.")
            self._send_none()
            return None
        ev_ref = super().handleNewSignals()
        if ev_ref:
            ev = self._logic.session.evidence(ev_ref)
            # Récupération de la raw_table puis transformation en Table d'Orange
            payload = ev.payload
            # Check if the table is empty
            if payload["rows"]:
                metas = []

                # Check if it's possible to convert to float a column
                for i, col in enumerate(payload["columns"]):
                    values = [row[col] for row in payload["rows"]]
                    if isinstance(values[0], (float, int)) and not isinstance(
                        values[0], bool
                    ):
                        metas.append(ContinuousVariable(col))
                    else:
                        metas.append(StringVariable(col))

                # Create the domain
                domain = Domain(attributes=[], metas=metas)

                # Création de la Table
                metas_array = np.array(
                    [
                        [row[col] for col in payload["columns"]]
                        for row in payload["rows"]
                        # if isinstance(row[col], str)
                        # else round(row[col], 8)
                        # for col in payload["columns"]
                    ],
                    dtype=object,
                )
                data_table = Table.from_numpy(
                    domain, X=np.empty((len(payload["rows"]), 0)), metas=metas_array
                )
                self.Outputs.data_table.send(data_table)
                return True
        self.Outputs.data_table.send(None)
        return True
        # LPC: Declare segmentation node wired from store node.
        # session_set_node(
        #     self.session,
        #     "features_<uuid8>",
        #     "StringFeatures",
        #     {},
        #     inputs={
        #         "strings": {
        #             "upstream_node": "filter_<uuid8>",
        #             "upstream_port": "string_view",
        #         },
        #     },
        # )

        # # LPC: Run and resolve output.
        # features_ref = _run_node_and_make_ref(
        #     self.session,
        #     node_id="features_<uuid8>",
        #     port="table",
        #     kind="table",
        # )
        # ev = self.session.store.get(features_ref.evidence_id)
        # display_text = _format_evidence_card(ev)
        # print(display_text)
        # # Récupération de la raw_table puis transformation en Table d'Orange
        # payload = ev.payload

        # # Création du domaine pour la Table de Orange
        # metas = [StringVariable(col) for col in payload["columns"]]
        # domain = Domain(attributes=[], metas=metas)

        # # Création de la Table
        # metas_array = np.array(
        #     [[row[col] for col in payload["columns"]] for row in payload["rows"]],
        #     dtype=object,
        # )
        # data_table = Table.from_numpy(
        #     domain, X=np.empty((len(payload["rows"]), 0)), metas=metas_array
        # )

        # self.Outputs.session.send(self.session)
        # self.Outputs.ref.send(features_ref)
        # self.Outputs.data_table.send(data_table)
        # return self.session, features_ref

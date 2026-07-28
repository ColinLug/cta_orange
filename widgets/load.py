"""
Orange Canvas Widget for the CTA's module.

It lets the user load a .TSV file from its local filesystem into the program.
Exposes it as an Orange Data Table too.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
from AnyQt.QtWidgets import QFileDialog
from Orange.data import ContinuousVariable, Domain, StringVariable, Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Output

from orangecta.cta_kernel.helpers.ref import CTARef
from orangecta.cta_kernel.helpers.session import CTASession
from orangecta.cta_kernel.helpers.widgets import OWCTAKernelBase


# pylint: disable=too-many-instance-attributes
class LoadTSVFile(OWCTAKernelBase):
    """The class for creating the files loader widget"""

    # Basic widget parameters
    name = "LoadTSV"
    description = "It lets the user load a .TSV file from its local filesystem into the program. \
    Exposes it as an Orange Data Table too."
    icon = "icons/load.png"
    priority = 10
    want_main_area = False
    resizing_enabled = True

    # OWCTAKernelBase widget parameters
    op_id = "LoadTSV"
    out_port = "raw_table"

    # Parameters/Settings of the LoadTSV widget
    path = Setting(".")
    dataset_id = Setting("wns_fixture_v0")
    slice_id = Setting("")
    document_role = Setting("messages")
    source_role = Setting("(chat,user)")
    lastLocation = Setting(".")

    class Outputs:
        """Outputs definition of the widget"""

        cta_data = Output("CTA Data", (CTASession, CTARef), auto_summary=False)
        data_table = Output("Table", Table)

    def __init__(self):
        """Manages the class creation. Basic UI is created here."""
        super().__init__()
        basicBox = gui.widgetBox(
            widget=self.controlArea,
            box="Source",
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
            value="path",
            orientation="horizontal",
            label="File path:",
            labelWidth=101,
            # callback=self.sendButton.settingsChanged,
            tooltip=("The path of the file."),
        )
        gui.separator(widget=basicBoxLine1, width=5)
        gui.button(
            widget=basicBoxLine1,
            master=self,
            label="Browse",
            callback=self.browse,
            tooltip=("Open a dialog for selecting file."),
        )
        gui.separator(widget=self.controlArea, width=5)

        # The scope modificator
        basicBox2 = gui.widgetBox(
            widget=self.controlArea,
            box="Scope labels",
            orientation="vertical",
        )
        basicBox2Line1 = gui.widgetBox(
            widget=basicBox2,
            box=False,
            orientation="horizontal",
        )
        gui.lineEdit(
            widget=basicBox2Line1,
            master=self,
            value="dataset_id",
            orientation="horizontal",
            label="Dataset :",
            labelWidth=101,
            tooltip=("Dataset ID to put in scope."),
        )
        gui.separator(widget=basicBox2, width=5)
        basicBox2Line2 = gui.widgetBox(
            widget=basicBox2,
            box=False,
            orientation="horizontal",
        )
        gui.lineEdit(
            widget=basicBox2Line2,
            master=self,
            value="slice_id",
            orientation="horizontal",
            label="Slice ID :",
            labelWidth=101,
            tooltip=("Slice ID to put in scope."),
        )
        gui.separator(widget=basicBox2, width=5)
        basicBox2Line3 = gui.widgetBox(
            widget=basicBox2,
            box=False,
            orientation="horizontal",
        )
        gui.lineEdit(
            widget=basicBox2Line3,
            master=self,
            value="document_role",
            orientation="horizontal",
            label="Document role :",
            labelWidth=101,
            tooltip=("Documents to put in scope."),
        )
        gui.separator(widget=basicBox2, width=5)
        basicBox2Line4 = gui.widgetBox(
            widget=basicBox2,
            box=False,
            orientation="horizontal",
        )
        gui.lineEdit(
            widget=basicBox2Line4,
            master=self,
            value="source_role",
            orientation="horizontal",
            label="Sources :",
            labelWidth=101,
            tooltip=("The sources to put in scope."),
        )

        gui.rubber(self.controlArea)
        self.sendButton = gui.button(
            widget=self.controlArea,
            master=self,
            label="Send",
            callback=self.sendData,
            tooltip=("Send the datas to process them."),
        )
        # Fix the widget's height to the minimum
        self.setFixedHeight(self.minimumSizeHint().height())

    def _params(self) -> Dict[str, Any]:
        """
        Collect widget parameters for the operator call.

        Returns:
            Dict[str, Any]: The parameters recorded onto the GraphSpec.
        """

        # Parameters are recorded into the GraphSpec and influence caching.
        return {"path": self.path}

    def _collect_inputs(self) -> Dict[str, Optional[CTARef]]:
        """
        Collect wiring inputs for the operator call.

        Returns:
            Dict[str, Optional[CTARef]]: Empty as this widget has no input.
        """
        return {}

    def _send_none(self) -> None:
        """Clear outputs of the load widget"""
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

    def handleNewSignals(self):
        """
        Sends the data to Output. Here it means the created CTASession object,
        as well as a CTARef to a table created and an orange data_table

        Returns:
            Optional[bool]: None if path is invalid, True otherwise
        """
        # Check si le chemin est bon (et est un .tsv)
        self.error()
        self.warning()
        if not Path(self.path).exists():
            self.error("Please provide a valid path.")
            self._send_none()
            return None
        elif not self.path.lower().endswith(".tsv"):
            self.error("Please provide a TSV file.")
            self._send_none()
            return None
        scope = self.createScope()
        profile_id = "comhum_v0"
        self._logic.session = CTASession.create(profile_id=profile_id, scope=scope)
        ev_ref = super().handleNewSignals()
        ev = self._logic.session.evidence(ev_ref)
        if ev:
            # Get raw_table and transformation it in an Orange Table
            payload = ev.payload
            # Check if the table is empty
            if payload["rows"]:
                metas = []
                metas_array = []

                # Check if it's possible to convert to float a column
                for _, col in enumerate(payload["columns"]):
                    values = [row[col] for row in payload["rows"]]
                    if isinstance(values[0], (float, int)) and not isinstance(
                        values[0], bool
                    ):
                        metas.append(ContinuousVariable(col))
                    else:
                        metas.append(StringVariable(col))

                # Domain creation
                domain = Domain(attributes=[], metas=metas)

                # Table creation
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

    def createScope(self):
        """
        Build the scope dict of the widget

        Returns:
            Dict[str, Any]: The scope to use to create a session.
        """

        if not (self.dataset_id and self.slice_id and self.document_role and self.source_role):
            self.warning("Some fields are empty. Don't forget to annotate them.")
        else: self.warning()
        scope = {
            "dataset_id": self.dataset_id,
            "slice_id": self.slice_id,
            "document_role": self.document_role,
            "source_role": self.source_role,
        }

        return scope

    def sendData(self):
        """Manual trigger for the Send button."""
        self.handleNewSignals()

    # From SuperTextFiles from textable.prototypes
    def browse(self):
        """Displays a FileDialog and lets the user select a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", self.lastLocation, "Text files (*)"
        )
        if not file_path:
            return
        self.path = os.path.normpath(file_path)
        self.lastLocation = file_path

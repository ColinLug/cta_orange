"""
Orange Canvas Widget for the CTA's module.

It lets the user load a .TSV file from its local filesystem into the program.
Exposes it as an Orange Data Table too.
"""

import os
from pathlib import Path
from typing import Any

from AnyQt.QtWidgets import QFileDialog
from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Output

from cta_orange.helpers.orange_datatable import create_orange_datatable
from cta_orange.helpers.ref import CTARef
from cta_orange.helpers.session import CTASession
from cta_orange.helpers.widgets import OWCTAKernelBase


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
    dataset_id = Setting("")
    slice_id = Setting("all_strings")
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
        gui.comboBox(
            widget=basicBox2Line2,
            master=self,
            value="slice_id",
            orientation="horizontal",
            label="Slice ID :",
            labelWidth=101,
            items=["all_strings"],
            tooltip=("Slice ID to put in scope."),
        )

        gui.rubber(self.controlArea)
        self.sendButton = gui.button(
            widget=self.controlArea,
            master=self,
            label="Send",
            callback=self.sendData,
            tooltip=("Send the data to process it."),
        )
        # Fix the widget's height to the minimum
        self.setFixedHeight(self.minimumSizeHint().height())

    def _params(self) -> dict[str, Any]:
        """
        Collect widget parameters for the operator call.

        Returns:
            dict[str, Any]: The parameters recorded onto the GraphSpec.
        """

        # Parameters are recorded into the GraphSpec and influence caching.
        return {"path": self.path}

    def _collect_inputs(self) -> dict[str, CTARef | None]:
        """
        Collect wiring inputs for the operator call.

        Returns:
            dict[str, Optional[CTARef]]: Empty as this widget has no input.
        """
        return {}

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

    def handleNewSignals(self):
        """
        Sends the data to Output. Here it means the created CTASession object,
        as well as a CTARef to a table created and an orange data_table

        Returns:
            Optional[bool]: None if path is invalid, True otherwise
        """
        # Check si le chemin est bon (et est un .tsv)
        self.error()
        self.information()
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
            payload = ev.payload
            if payload:
                data_table = create_orange_datatable(payload["rows"], payload["columns"])
                self.Outputs.data_table.send(data_table)
                return True
        self.Outputs.data_table.send(None)
        return True

    def createScope(self):
        """
        Build the scope dict of the widget

        Returns:
            dict[str, Any]: The scope to use to create a session.
        """
        if not self.dataset_id:
            self.information("Dataset ID is empty. Don't forget to annotate it.")
        else: self.information()
        scope = {
            "dataset_id": self.dataset_id,
            "slice_id": self.slice_id,
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

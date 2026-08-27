"""Orange Canvas Widget for the CTA's module. Helps view some of
the evidences created by the widgets"""

import json
from typing import Optional

from AnyQt.QtWidgets import QTextBrowser
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Input, OWWidget
from cta_kernel.runtime.evidence import Evidence

from cta_orange.helpers.ref import CTARef
from cta_orange.helpers.session import CTASession

_MAX_PAYLOAD_CHARS = 2000

def _truncate(text: str, length: int = 40) -> str:
    """Truncate text to length, appending '...' only if actually truncated."""
    return text if len(text) <= length else text[:length] + "..."

class EvidenceBrowserCTA(OWWidget):
    """Widget that displays the content of the evidence received from upstream, and optionally all other evidence in the session."""
    # Widget's name as displayed in the canvas
    name = "Evidence Browser"
    # Short widget description
    description = "Lets the user browse and inspect evidence produced by upstream widgets."

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/evidence_browser.png"
    priority = 10

    class Inputs:
        """Inputs definition of the widget"""

        cta_data = Input("CTA Data", (CTASession, CTARef), auto_summary=False)

    want_main_area = False
    resizing_enabled = True
    displayBool = False
    payloadBool = False

    def __init__(self):
        """Manages the class creation. Basic UI is created here."""
        super().__init__()
        self.session = None
        self.ref: Optional[CTARef] = None
        self.payloadCheck = gui.checkBox(
            widget=self.controlArea,
            master=self,
            value="payloadBool",
            label="Display payload",
            callback=self.displayEvidence,
        )
        basicBox = gui.widgetBox(
            widget=self.controlArea,
            box="Evidence",
            orientation="vertical",
        )
        self.browser = QTextBrowser()
        basicBox.layout().addWidget(self.browser)
        self.prevEvCheck = gui.checkBox(
            widget=self.controlArea,
            master=self,
            value="displayBool",
            label="Display upstream evidence",
            callback=self.displayPrev,
        )
        self.prevEvBox = basicBox = gui.widgetBox(
            widget=self.controlArea,
            box="Upstream evidence",
            orientation="vertical",
        )
        self.browserPrev = QTextBrowser()
        self.prevEvBox.layout().addWidget(self.browserPrev)
        self.prevEvBox.setVisible(False)

    @Inputs.cta_data
    def set_ctaData(self, cta_data: Optional[tuple]) -> None:  # noqa: D401
        """Receive the upstream CTAData : the session and a ref to the upstream claim"""
        # Store the new ref and trigger recomputation if possible.
        session, ref = cta_data if cta_data is not None else (None,None)
        self.session = session
        self.ref = ref
        self.displayEvidence()

    def displayPrev(self):
        """Toggle visibility of the upstream-evidence panel and refresh it if shown."""
        if self.displayBool:
            self.displayEvidence()
            self.prevEvBox.setVisible(True)
        else:
            self.prevEvBox.setVisible(False)

    def formatEvidence(self, ev: Evidence, displayPayload: bool = True):
        """Format a string representation of one evidence entry for display.

        Args:
            ref_ev (str): a ref to an evidence
            displayPayload (bool): if the payload should be displayed

        Returns:
            str: The formatted string to be displayed
        """
        str_ev = (
            "Evidence ID:\n    " + _truncate(ev.evidence_id) + "\n" +"-" * 35 + "\n\n"
        )
        str_ev += (
            "Origin node ID:\n    "
            + ev.prov.origin_node_id[:40]
            + "\n"
            + "-" * 35
            + "\n\n"
        )
        str_ev += "Kind:\n    " + ev.type_id + "\n"
        if self.payloadBool and displayPayload:
            payload_str = json.dumps(ev.payload, indent=4, ensure_ascii=False)
            if len(payload_str) > _MAX_PAYLOAD_CHARS:
                payload_str = payload_str[:_MAX_PAYLOAD_CHARS] + f"\n... [truncated, {len(payload_str)} chars total]"
            str_ev += (
                "-" * 35
                + "\n\n"
                + "Payload:\n    "
                + payload_str
                + "\n\n"
            )
        else:
            str_ev += "\n"
        str_ev += "=" * 60 + "\n"
        return str_ev

    def displayEvidence(self):
        """Render the current evidence (and, if enabled, all other evidence in the session) into the text browsers."""
        # Set the text inside the widget to display the connected/received ref
        self.browser.clear()
        if self.ref:
            str_ev = self.formatEvidence(self.session.evidence(self.ref))
            self.browser.append(str_ev)

        # Set the text inside the widget to display all sessions ref
        if self.displayBool and self.session is not None and self.ref is not None:
            self.browserPrev.clear()
            list_evidences = self.session.all_evidence()
            parts = [self.formatEvidence(ev) for ev in list_evidences if ev != self.session.evidence(self.ref)]
            self.browserPrev.setPlainText("".join(parts))

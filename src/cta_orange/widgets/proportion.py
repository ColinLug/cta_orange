"""Orange Canvas Widget for the CTA's module. Calculates a proportion
of strings from a predicate"""

from typing import Any, Optional

from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Input, Output

from cta_orange.helpers.ref import CTARef
from cta_orange.helpers.session import CTASession
from cta_orange.helpers.widgets import OWCTAKernelBase


class CTAProportion(OWCTAKernelBase):
    """The class for creating the proportion widget"""
    # Widget's name as displayed in the canvas
    name = "Proportion"
    # Short widget description
    description = "Calculates a proportion of strings from a predicate"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/proportion.png"

    priority = 10

    # Widget's outputs; here, a single output named "Number", of type int
    class Inputs:
        """Inputs definition of the widget"""

        cta_data = Input("CTA Data", (CTASession, CTARef), auto_summary=False)

    class Outputs:
        """Outputs definition of the widget"""

        cta_data = Output("CTA Data", (CTASession, CTARef), auto_summary=False)

    op_id = "Proportion"
    out_port = "scalar"

    num_predicate = Setting("")
    mode = Setting("mass")
    want_main_area = False
    resizing_enabled = True

    def __init__(self):
        """Manages the class creation. Basic UI is created here."""
        super().__init__()
        self.ref: Optional[CTARef] = None
        basicBox = gui.widgetBox(
            widget=self.controlArea,
            box="Proportion",
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
            value="num_predicate",
            orientation="horizontal",
            label="Compute proportion where:",
            labelWidth=200,
            # callback=self.sendButton.settingsChanged,
            tooltip=("The conditions the strings shall meet to be counted."),
        )
        gui.separator(widget=basicBox, width=3)
        gui.rubber(self.controlArea)
        sendButton = gui.button(
            widget=self.controlArea,
            master=self,
            label="Send",
            callback=self.sendData,
            tooltip=("Send the data to process it."),
        )
        # Fix the widget's height to the minimum
        self.setFixedHeight(self.minimumSizeHint().height())

    @Inputs.cta_data
    def set_ctaData(self, cta_data: Optional[tuple]) -> None:  # noqa: D401
        """Receive the upstream CTAData : the session and a ref to the upstream filtered strings"""

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
        return {"predicate": self.num_predicate, "mode": self.mode}

    def _collect_inputs(self) -> dict[str, Optional[CTARef]]:
        """
        Collect wiring inputs for the operator call.

        Returns:
            dict[str, Optional[CTARef]]: the ref to the filtered strings received from StringsFilter
        """
        return {"denom": self.ref}

    def _send_none(self) -> None:
        """Clear outputs of the widget"""
        self.Outputs.cta_data.send((None, None))
        # self.Outputs.data_table.send(None)

    def _send_ref(self, ref):
        """
        Sends the session and the ref to output.

        Args:
            ref (CTARef): the reference to the evidence to send

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
        as well as a CTARef to a proportion.

        Returns:
            Optional[CTARef]: None if no upstream or invalid predicate, the ref to evidence otherwise
        """
        self.error()
        self.information()
        # Check the upstream is linked
        if self.ref is None or self._logic.session is None:
            self.error("No upstream data connected.")
            self._send_none()
            return None

        # Check if predicate is empty
        if not self.num_predicate.strip():
            self.information("No predicate configured yet.")
            self._send_none()
            return None

        ev_ref = super().handleNewSignals()
        return ev_ref

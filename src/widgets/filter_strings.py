"""Orange Canvas Widget for the CTA's module. Filter strings using a predicate"""

from typing import Any, Optional

from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Input, Output

from orangecta.cta_kernel.operators.predicate_dsl import parse_predicate
from orangecta.cta_kernel.helpers.ref import CTARef
from orangecta.cta_kernel.helpers.session import CTASession
from orangecta.cta_kernel.helpers.widgets import OWCTAKernelBase


class StringsFilter(OWCTAKernelBase):
    """Widget that filters strings using a predicate"""
    # Widget's name as displayed in the canvas
    name = "Filter Strings"
    # Short widget description
    description = "Filter strings using a predicate"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/filterstrings.png"

    priority = 10

    # Widget's outputs; here, a single output named "Number", of type int
    class Inputs:
        """Inputs definition of the widget"""

        cta_data = Input("CTA Data", (CTASession, CTARef), auto_summary=False)

    class Outputs:
        """Outputs definition of the widget"""

        cta_data = Output("CTA Data", (CTASession, CTARef), auto_summary=False)

    op_id = "FilterStrings"
    out_port = "string_view"
    predicate = Setting("")
    want_main_area = False
    resizing_enabled = True

    def __init__(self):
        """Manages the class creation. Basic UI is created here."""
        super().__init__()
        self.ref: Optional[CTARef] = None
        basicBox = gui.widgetBox(
            widget=self.controlArea,
            box="Filter Options",
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
            value="predicate",
            orientation="horizontal",
            label="Including strings where:",
            labelWidth=150,
            # callback=self.sendButton.settingsChanged,
            tooltip=("The conditions the strings shall meet to not be filtered out."),
        )
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
        return {"predicate": self.predicate}

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
        # self.Outputs.data_table.send(None)

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
        as well as a CTARef to the resulting filtered string view.

        Returns:
            Optional[CTARef]: None if no upstream or invalid predicate, the ref to the evidence otherwise
        """
        self.error()
        self.warning()
        # Check the upstream is linked
        if self.ref is None or self._logic.session is None:
            self.error("No upstream data connected.")
            self._send_none()
            return None

        # Check if predicate is empty
        if not self.predicate.strip():
            self.warning("No predicate configured yet.")
            self._send_none()
            return None

        # Check the validity of the predicate
        try:
            parse_predicate(self.predicate)
        except ValueError as exc:
            self.error(f"Invalid predicate: {exc}")
            self._send_none()
            return None
        # if len(self.predicate) > 200:
        #     self.warning("Predicate is very long. It can cause slowness or issues. Consider providing a shorter predicate.")
        ev_ref = super().handleNewSignals()
        return ev_ref
        # LPC: Declare segmentation node wired from store node.
        # session_set_node(
        #     self.session,
        #     "filter_<uuid8>",
        #     "FilterStrings",
        #     {"predicate": self.predicate},
        #     inputs={
        #         "strings": {
        #             "upstream_node": "seg",
        #             "upstream_port": "string_view",
        #         },
        #     },
        # )

        # # LPC: Run and resolve output.
        # filter_ref = _run_node_and_make_ref(
        #     self.session,
        #     node_id="filter_<uuid8>",
        #     port="string_view",
        #     kind="string_view",
        # )
        # self.Outputs.session.send(self.session)
        # self.Outputs.ref.send(filter_ref)
        # return self.session, filter_ref

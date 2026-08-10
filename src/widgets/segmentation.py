"""Orange Canvas Widget for the CTA's module. Segment the strings into chars,
or using a certain delimiter"""

from typing import Any, Optional

from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Input, Output

from orangecta.cta_kernel.helpers.ref import CTARef
from orangecta.cta_kernel.helpers.session import CTASession
from orangecta.cta_kernel.helpers.widgets import OWCTAKernelBase


class CTASegmentation(OWCTAKernelBase):
    """Widget that segments strings from a string store."""
    # Widget's name as displayed in the canvas
    name = "Segmentation"
    # Short widget description
    description = "Segment the strings into chars, or using a certain delimiter."

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/segmentation.png"

    priority = 10

    # Widget's outputs; here, a single output named "Number", of type int
    class Inputs:
        """Inputs definition of the widget"""

        cta_data = Input("CTA Data", (CTASession, CTARef), auto_summary=False)

    class Outputs:
        """Outputs definition of the widget"""

        cta_data = Output("CTA Data", (CTASession, CTARef), auto_summary=False)
        # data_table = Output("Table", Table)

    op_id = "Segmentation"
    out_port = "string_view"

    mode = Setting("chars")
    delimiter = Setting("-")
    want_main_area = False
    resizing_enabled = False

    def __init__(self):
        """Manages the class creation. Basic UI is created here."""
        super().__init__()
        self.ref: Optional[CTARef] = None
        basicBox = gui.widgetBox(
            widget=self.controlArea,
            box="Segmentation Options",
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
            items=["chars", "delimiter"],
            label="Mode :",
            callback=self.changeMode,
            labelWidth=101,
            sendSelectedValue=True,
        )
        self.delimiterLine = gui.widgetBox(
            widget=basicBox,
            box=False,
            orientation="horizontal",
        )
        gui.lineEdit(
            widget=self.delimiterLine,
            master=self,
            value="delimiter",
            orientation="horizontal",
            label="Delimiter :",
            labelWidth=100,
            # callback=self.sendButton.settingsChanged,
            tooltip=("The delimiter to use for cutting strings."),
        )
        gui.rubber(self.controlArea)
        sendButton = gui.button(
            widget=self.controlArea,
            master=self,
            label="Send",
            callback=self.sendData,
            tooltip=("Send the data to process it."),
        )
        self.delimiterLine.setVisible(False)

    @Inputs.cta_data
    def set_ctaData(self, cta_data: Optional[tuple]) -> None:
        """Receive the upstream CTAData : the session and a ref to the upstream strings store"""

        # Store the new ref and trigger recomputation if possible.
        session, ref = cta_data if cta_data is not None else (None,None)
        self._logic.session = session
        self.ref = ref

    def changeMode(self):
        """Show or hide the delimiter field depending on the selected mode."""
        if self.mode == "delimiter":
            self.delimiterLine.setVisible(True)
        else:
            self.delimiterLine.setVisible(False)

    def _params(self) -> dict[str, Any]:
        """
        Collect widget parameters for the operator call.

        Returns:
            dict[str, Any]: The parameters recorded onto the GraphSpec.
        """
        # Parameters are recorded into the GraphSpec and influence caching.
        params = {"policy_id": 0, "mode": self.mode}
        if self.mode == "delimiter":
            params["delimiter"] = self.delimiter
        return params

    def _collect_inputs(self) -> dict[str, Optional[CTARef]]:
        """
        Collect wiring inputs for the operator call.

        Returns:
            dict[str, Optional[CTARef]]: the ref to the strings store received from ExtractStringsCTA
        """
        return {"strings": self.ref}

    def _send_none(self) -> None:
        """Clear outputs of the load widget"""
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
        as well as a CTARef to a segmentation.

        Returns:
            Optional[CTARef]: The ref to the created Segmentation or None
        """
        self.error()
        self.warning()
        if self.ref is None or self._logic.session is None:
            self.error("No upstream data connected.")
            self._send_none()
            return None

        if self.mode == "delimiter" and not self.delimiter:
            self.error("The delimiter is empty, please use \"chars\" mode or provide a legitimate delimiter.")
            self._send_none()
            return None
        ev_ref = super().handleNewSignals()
        return ev_ref
        # LPC: Declare segmentation node wired from store node.
        # session_set_node(
        #     self.session,
        #     "seg",
        #     "Segmentation",
        #     {"policy_id": 0, "mode": self.mode},
        #     inputs={
        #         "strings": {
        #             "upstream_node": "store",
        #             "upstream_port": "string_store",
        #         },
        #     },
        # )

        # # LPC: Run and resolve output.
        # seg_ref = _run_node_and_make_ref(
        #     self.session, node_id="seg", port="string_view", kind="string_view"
        # )
        # self.Outputs.session.send(self.session)
        # self.Outputs.ref.send(seg_ref)
        # return self.session, seg_ref

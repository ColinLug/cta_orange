"""Acceptance tests for the ratified CTA Orange 0.1.1 corrective release."""

from Orange.widgets.tests.base import WidgetTest

from cta_orange.widgets.ev_browser import EvidenceBrowserCTA
from cta_orange.widgets.segmentation import CTASegmentation
from cta_orange.widgets.string_features import CTAStringsFeatures


class TestStringsFeaturesOrdering(WidgetTest):
    """Require explicit, persisted exposure of the kernel ordering parameter."""

    def test_default_ordering_is_count_desc(self):
        """A legacy workflow without saved ordering keeps 0.1.0 semantics."""
        widget = self.create_widget(CTAStringsFeatures, stored_settings={})

        self.assertEqual(widget.order_by, "count_desc")
        self.assertEqual(widget._params()["order_by"], "count_desc")

    def test_ordering_control_exposes_exact_kernel_domain(self):
        """The visible selector exposes all and only supported kernel values."""
        widget = self.create_widget(CTAStringsFeatures)
        values = [
            widget.orderCombo.itemData(index)
            for index in range(widget.orderCombo.count())
        ]

        self.assertEqual(
            values,
            [
                "count_desc",
                "count_asc",
                "len_desc",
                "len_asc",
                "variety_desc",
                "variety_asc",
            ],
        )

    def test_saved_ordering_is_restored_and_passed_to_kernel(self):
        """Orange restoration and kernel parameter mapping agree."""
        widget = self.create_widget(
            CTAStringsFeatures,
            stored_settings={"top_k": 20, "order_by": "len_desc"},
        )

        self.assertEqual(widget.order_by, "len_desc")
        self.assertEqual(widget.orderCombo.currentData(), "len_desc")
        self.assertEqual(
            widget._params(),
            {"top_k": 20, "order_by": "len_desc"},
        )


class TestSegmentationRestoredVisibility(WidgetTest):
    """Require the delimiter field to reflect restored mode immediately."""

    def test_restored_delimiter_mode_shows_delimiter_field(self):
        """A delimiter workflow opens with its delimiter control exposed."""
        widget = self.create_widget(
            CTASegmentation,
            stored_settings={"mode": "delimiter", "delimiter": "|"},
        )

        self.assertEqual(widget.mode, "delimiter")
        self.assertEqual(widget.delimiter, "|")
        self.assertFalse(widget.delimiterLine.isHidden())
        self.assertEqual(widget._params(), {"mode": "delimiter", "delimiter": "|"})

    def test_restored_chars_mode_hides_delimiter_field(self):
        """A chars workflow opens with the irrelevant delimiter control hidden."""
        widget = self.create_widget(
            CTASegmentation,
            stored_settings={"mode": "chars", "delimiter": "|"},
        )

        self.assertEqual(widget.mode, "chars")
        self.assertTrue(widget.delimiterLine.isHidden())
        self.assertEqual(widget._params(), {"mode": "chars"})


class TestEvidenceBrowserPayloadSetting(WidgetTest):
    """Require payload display to use a safe default and remain restorable."""

    def test_new_browser_hides_payload_by_default(self):
        """A fresh browser starts with Display payload unchecked."""
        widget = self.create_widget(EvidenceBrowserCTA, stored_settings={})

        self.assertFalse(widget.payloadBool)
        self.assertFalse(widget.payloadCheck.isChecked())
        self.assertFalse(widget.displayBool)

    def test_saved_payload_choice_is_restored(self):
        """A saved unchecked payload choice survives Orange restoration."""
        widget = self.create_widget(
            EvidenceBrowserCTA,
            stored_settings={"payloadBool": False},
        )

        self.assertFalse(widget.payloadBool)
        self.assertFalse(widget.payloadCheck.isChecked())
        self.assertFalse(widget.displayBool)

    def test_saved_checked_payload_choice_is_restored(self):
        """A saved checked payload choice survives Orange restoration."""
        widget = self.create_widget(
            EvidenceBrowserCTA,
            stored_settings={"payloadBool": True},
        )

        self.assertTrue(widget.payloadBool)
        self.assertTrue(widget.payloadCheck.isChecked())
        self.assertFalse(widget.displayBool)

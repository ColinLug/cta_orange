import pytest
from Orange.widgets.tests.base import WidgetTest
from unittest.mock import MagicMock

from cta_orange.widgets.ev_browser import EvidenceBrowserCTA, _truncate


def test_truncate():
    """Test the truncate string function"""
    assert _truncate("Short text") == "Short text"
    assert _truncate("Shorter text", 7) == "Shorter..."

class TestClaimWidget(WidgetTest):
    """Tests for EvidenceBrowserCTA"""

    def setUp(self):
        """Prepare for the test."""
        # Création du widget avec les helpers Orange
        self.widget = self.create_widget(EvidenceBrowserCTA)

    def test_displayPrev(self):
        """Test if changing the check changes display visibility"""
        self.widget.displayEvidence = MagicMock()
        self.widget.prevEvBox.setVisible = MagicMock()
        self.widget.displayBool = True
        self.widget.displayPrev()
        self.widget.prevEvBox.setVisible.assert_called_with(True)
        self.widget.displayBool = False
        self.widget.displayPrev()
        self.widget.prevEvBox.setVisible.assert_called_with(False)

    def test_format_evidence_payload_toggle(self):
        """Payload block only appears when payloadBool is True"""
        ev = MagicMock(evidence_id="abc123", type_id="Table")
        ev.prov.origin_node_id = "node_1"
        ev.payload = {"rows": [1, 2, 3]}

        self.widget.payloadBool = False
        self.assertNotIn("Payload:", self.widget.formatEvidence(ev))

        self.widget.payloadBool = True
        self.assertIn("Payload:", self.widget.formatEvidence(ev))

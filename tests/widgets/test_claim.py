from os import wait

import pytest
from Orange.widgets.tests.base import WidgetTest
from unittest.mock import MagicMock

from cta_orange.widgets.claim import OrangeCTAClaim, _single_line


def test_single_line():
    assert _single_line("Multi\nlines\ntext") == "Multi lines text"
    assert _single_line("") ==""


class TestClaimWidget(WidgetTest):
    """Tests for OrangeCTAClaim."""

    def setUp(self):
        """Prepare for the test"""
        # Création du widget avec les helpers Orange
        self.widget = self.create_widget(OrangeCTAClaim)
        self.widget.error = MagicMock()
        self.widget.information = MagicMock()

    def test_change_mode_compare(self):
        """Test if changing mode works when in Compare"""
        self.widget.delimiterLineDelta.setVisible = MagicMock()
        self.widget.delimiterLineTheta.setVisible = MagicMock()
        self.widget.mode = "Compare"
        self.widget.changeMode()
        self.widget.delimiterLineDelta.setVisible.assert_called_with(True)
        self.widget.delimiterLineTheta.setVisible.assert_called_with(False)

    def test_change_mode_threshold(self):
        """Test if changing mode works when in Threshold"""
        self.widget.delimiterLineDelta.setVisible = MagicMock()
        self.widget.delimiterLineTheta.setVisible = MagicMock()
        self.widget.mode = "Threshold"
        self.widget.changeMode()
        self.widget.delimiterLineDelta.setVisible.assert_called_with(False)
        self.widget.delimiterLineTheta.setVisible.assert_called_with(True)

    def test_handle_new_signals_missing_input(self):
        """Test handleNewSignals when input is missing"""
        self.widget.scalar_a = None
        result = self.widget.handleNewSignals()
        self.assertIsNone(result)
        self.widget.error.assert_called_with("Upstream data(s) are not connected.")

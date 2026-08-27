from unittest.mock import MagicMock

from Orange.widgets.tests.base import WidgetTest

from cta_orange.widgets.string_features import CTAStringsFeatures


class TestFeaturesWidget(WidgetTest):
    """Tests for CTAStringsFeatures."""

    def setUp(self):
        """Prepare for the test"""
        # Création du widget avec les helpers Orange
        self.widget = self.create_widget(CTAStringsFeatures)
        self.widget.error = MagicMock()
        self.widget.information = MagicMock()

    def test_handle_new_signals_missing_input(self):
        """Test handleNewSignals when input is missing"""
        self.widget.ref = None
        self.widget._logic.session = MagicMock()
        result = self.widget.handleNewSignals()
        self.assertIsNone(result)
        self.widget.error.assert_called_with("No upstream data connected.")

        self.widget.ref = MagicMock()
        self.widget._logic.session = None
        result = self.widget.handleNewSignals()
        self.assertIsNone(result)
        self.widget.error.assert_called_with("No upstream data connected.")

    def test_handle_new_signals_top_k(self):
        """Test handleNewSignals when top_k is not an positive integer"""
        self.widget.ref = MagicMock()
        self.widget._logic.session = MagicMock()
        self.widget.top_k = -1
        result = self.widget.handleNewSignals()
        self.assertIsNone(result)
        self.widget.error.assert_called_with("Top k must be a positive integer.")

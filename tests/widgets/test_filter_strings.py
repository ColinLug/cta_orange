from unittest.mock import MagicMock

from Orange.widgets.tests.base import WidgetTest

from cta_orange.widgets.filter_strings import StringsFilter


class TestFilterWidget(WidgetTest):
    """Tests for StringsFilter."""

    def setUp(self):
        """Prepare for the test"""
        # Création du widget avec les helpers Orange
        self.widget = self.create_widget(StringsFilter)
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

    def test_predicate_empty(self):
        """Test handleNewSignals when predicate is empty"""
        self.widget.ref = MagicMock()
        self.widget._logic.session = MagicMock()
        self.widget.predicate = ""
        result = self.widget.handleNewSignals()
        self.assertIsNone(result)
        self.widget.information.assert_called_with("No predicate configured yet.")

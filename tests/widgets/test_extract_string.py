
from unittest.mock import MagicMock

from Orange.widgets.tests.base import WidgetTest

from cta_orange.widgets.extract_string import ExtractStringsCTA


class TestExtractStringWidget(WidgetTest):
    """Tests for ExtractStringsCTA."""

    def setUp(self):
        """Prepare for the test"""
        self.widget = self.create_widget(ExtractStringsCTA)
        self.widget.error = MagicMock()

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

    def test_handle_new_signals_wrong_column_name(self):
        """Test handleNewSignals when column name is not in Table"""
        self.widget.ref = MagicMock()
        self.widget._logic.session = MagicMock()
        fake_ev = MagicMock()
        fake_ev.payload={"columns": ["a","b","c"]}
        self.widget._logic.session.evidence.return_value = fake_ev

        self.widget.string_col = "d"
        self.widget.source_id_cols = "b    , c"
        result = self.widget.handleNewSignals()
        self.assertIsNone(result)
        self.widget.error.assert_called_with("Column(s) not found in upstream table: d")

        self.widget.string_col = "a"
        self.widget.source_id_cols = "d,e"
        result = self.widget.handleNewSignals()
        self.assertIsNone(result)
        self.widget.error.assert_called_with("Column(s) not found in upstream table: d, e")

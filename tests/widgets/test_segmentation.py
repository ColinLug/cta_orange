from unittest.mock import MagicMock

from Orange.widgets.tests.base import WidgetTest

from cta_orange.widgets.segmentation import CTASegmentation


class TestSegWidget(WidgetTest):
    """Tests for CTASegmentation."""

    def setUp(self):
        """Prepare for the test"""
        # Création du widget avec les helpers Orange
        self.widget = self.create_widget(CTASegmentation)
        self.widget.error = MagicMock()
        self.widget.information = MagicMock()

    def test_change_mode(self):
        """Test if changing mode works"""
        self.widget.delimiterLine.setVisible = MagicMock()
        self.widget.mode = "delimiter"
        self.widget.changeMode()
        self.widget.delimiterLine.setVisible.assert_called_with(True)

        self.widget.mode = "chars"
        self.widget.changeMode()
        self.widget.delimiterLine.setVisible.assert_called_with(False)

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

    def test_handle_new_signals_missing_delimiter(self):
        """Test handleNewSignals when in delimiter mode and delimiter is missing"""
        self.widget.delimiter = ""
        self.widget.mode = "delimiter"
        self.widget.ref = MagicMock()
        self.widget._logic.session = MagicMock()
        result = self.widget.handleNewSignals()
        self.assertIsNone(result)
        self.widget.error.assert_called_with("The delimiter is empty, please use \"chars\" mode or provide a legitimate delimiter.")

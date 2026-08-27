import pytest
from pathlib import Path
from Orange.widgets.tests.base import WidgetTest
from unittest.mock import MagicMock, patch

from cta_orange.widgets.load import LoadTSVFile



class TestClaimWidget(WidgetTest):
    """Tests for LoadTSVFile."""

    def setUp(self):
        """Prepare for the test"""
        # Création du widget avec les helpers Orange
        self.widget = self.create_widget(LoadTSVFile)
        self.widget.error = MagicMock()
        self.widget.information = MagicMock()

    def test_create_scope(self):
        """Test if the information is displayed when creating a scope with empty strings"""
        self.widget.dataset_id = ""
        self.widget.slice_id = "all_strings"
        scope = self.widget.createScope()
        assert scope == {"dataset_id": "", "slice_id": "all_strings",}
        self.widget.information.assert_called_with("Dataset ID is empty. Don't forget to annotate it.")

    def test_handle_new_signals_invalid_path(self):
        """Test if the errors in the path are correctly reported"""
        self.widget.path = "false/path/houplahoup.tsv"
        result = self.widget.handleNewSignals()
        self.assertIsNone(result)
        self.widget.error.assert_called_with("Please provide a valid path.")

        self.widget.path = "tests/widgets/test_load.py"
        result = self.widget.handleNewSignals()
        self.assertIsNone(result)
        self.widget.error.assert_called_with("Please provide a TSV file.")

    @patch("cta_orange.widgets.load.QFileDialog.getOpenFileName")
    def test_browse(self, mock_dialog):
        """Test if the browse method is working as intended"""
        mock_dialog.return_value = ("/path/file.tsv", "")
        self.widget.browse()
        assert self.widget.path == "/path/file.tsv"

        mock_dialog.return_value = ("", "")
        self.widget.path = "old/path.tsv"
        self.widget.browse()
        assert self.widget.path == "old/path.tsv"

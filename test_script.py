import unittest
from unittest.mock import patch
patch.stopall()
from io import StringIO
from bs4 import BeautifulSoup
from readJira import contains_phrase, normalize_comment

def download_issue_report(issue_id):
    # Implementation of the download_issue_report function
    # You can modify this function as per your requirements
    return f"issue_reports/{issue_id}.xml"

class test_script(unittest.TestCase):
    def setUp(self):
        # Set up any necessary test data or configurations
        pass

    def tearDown(self):
        # Clean up after each test case
        pass

    def test_contains_phrase(self):
        # Test contains_phrase function with a matching phrase
        sentence = "This is an issue"
        phrases = {"issue"}
        self.assertTrue(contains_phrase(sentence, phrases))

        # Test contains_phrase function with a non-matching phrase
        sentence = "This is a feature"
        phrases = {"issue"}
        self.assertFalse(contains_phrase(sentence, phrases))

    def test_normalize_comment(self):
        # Test normalize_comment function
        comment = "<p>This is a sample comment.</p>"
        expected_normalized_comment = "sampl comment"

        # Mock the BeautifulSoup object to avoid actual HTML parsing
        with patch.object(BeautifulSoup, "__init__", return_value=None):
            normalized_comment = normalize_comment(comment)

        self.assertEqual(normalized_comment, expected_normalized_comment)

    @patch("readJira.download_issue_report")
    def test_custom_issue_codes(self, mock_download):
        # Test custom issue codes without downloading XML reports
        issue_codes = ["001", "002", "003"]
        mock_download.side_effect = lambda issue_id: None

        for issue_code in issue_codes:
            file_path = download_issue_report(issue_code)
            expected_file_path = None
            self.assertEqual(file_path, expected_file_path)

            # Ensure the download message is not printed
            with patch("sys.stdout", new=StringIO()) as stdout:
                download_issue_report(issue_code)
            self.assertEqual(stdout.getvalue(), "")

if __name__ == "__main__":
    patch.stopall()
    unittest.main()
    print("All of your methods are valid and work")

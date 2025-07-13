import unittest
from unittest.mock import patch, mock_open, MagicMock

from app.services.document_processing import chunk_text, extract_text_from_txt, extract_text_from_pdf

class TestDocumentProcessing(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="Sample text file content.")
    def test_extract_text_from_txt(self, mock_file):
        result = extract_text_from_txt("dummy.txt")
        self.assertEqual(result, "Sample text file content.")
        mock_file.assert_called_once_with("dummy.txt", "r", encoding="utf-8")

    @patch("app.services.document_processing.PdfReader")
    @patch("builtins.open", new_callable=mock_open)
    def test_extract_text_from_pdf(self, mock_file, mock_pdf_reader):
        mock_pdf_reader.return_value.pages = [
            MagicMock(extract_text=MagicMock(return_value="Page 1 text")),
            MagicMock(extract_text=MagicMock(return_value="Page 2 text"))
        ]
        result = extract_text_from_pdf("dummy.pdf")
        self.assertEqual(result, "Page 1 textPage 2 text")

    def test_chunk_text(self):
        sample_text = "A" * 2500  # Long enough to chunk
        chunks = chunk_text(sample_text, chunk_size=1000, chunk_overlap=200)
        self.assertTrue(len(chunks) >= 2)
        self.assertTrue(all(len(chunk) <= 1000 for chunk in chunks))

if __name__ == "__main__":
    unittest.main()
import fitz  # PyMuPDF
import docx
import docx2txt
import os
from typing import Optional

class FileProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Optional[str]:
        try:
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return None

    @staticmethod
    def extract_text_from_docx(file_path: str) -> Optional[str]:
        try:
            text = docx2txt.process(file_path)
            return text
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return None

    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        if file_path.endswith('.pdf'):
            return FileProcessor.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            return FileProcessor.extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
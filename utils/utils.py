# utils.py
import os
import re
import logging
import hashlib
from datetime import datetime
from typing import Optional, Set, Dict, Union, List
import docx2txt
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import magic
import chardet
from collections import Counter
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileProcessingError(Exception):
    """Custom exception for file processing errors."""
    pass

class FileHandler:
    """Handles file operations such as hashing, MIME type detection, and encoding."""
    ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx', '.doc'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Generate SHA-256 hash of file content."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            raise FileProcessingError(f"Hash calculation failed: {e}")

    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """Detect real file type using python-magic."""
        try:
            return magic.from_file(file_path, mime=True)
        except Exception as e:
            logger.error(f"Error detecting MIME type for {file_path}: {e}")
            raise FileProcessingError(f"MIME type detection failed: {e}")

    @staticmethod
    def detect_encoding(file_path: str) -> str:
        """Detect character encoding of text file using chardet."""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            return chardet.detect(raw_data)['encoding']
        except Exception as e:
            logger.error(f"Error detecting encoding for {file_path}: {e}")
            raise FileProcessingError(f"Encoding detection failed: {e}")

class TextExtractor:
    """Class for extracting text from various file types."""
    
    def __init__(self):
        self.supported_formats = {
            '.txt': self._extract_from_txt,
            '.pdf': self._extract_from_pdf,
            '.docx': self._extract_from_docx,
            '.doc': self._extract_from_docx  # Assuming .doc files can be handled by docx2txt
        }

    def extract_text(self, file_path: str) -> str:
        """Main method to extract text based on file type."""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.supported_formats:
                raise FileProcessingError(f"Unsupported file format: {file_ext}")

            # Verify file size
            if os.path.getsize(file_path) > FileHandler.MAX_FILE_SIZE:
                raise FileProcessingError("File size exceeds maximum limit")

            # Extract text using appropriate method
            text = self.supported_formats[file_ext](file_path)
            return self.clean_text(text)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise FileProcessingError(f"Error processing file: {str(e)}")

    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT files."""
        encoding = FileHandler.detect_encoding(file_path)
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            logger.warning(f"Failed to decode with {encoding}, trying utf-8")
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files with OCR fallback for images."""
        try:
            text = ""
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if not page_text.strip():
                        # If no text extracted, try OCR
                        text += self._ocr_pdf_page(file_path, reader.pages.index(page))
                    else:
                        text += page_text
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise FileProcessingError(f"PDF extraction failed: {str(e)}")

    def _ocr_pdf_page(self, pdf_path: str, page_number: int) -> str:
        """Perform OCR on a PDF page."""
        try:
            images = convert_from_path(pdf_path, first_page=page_number + 1, last_page=page_number + 1)
            if images:
                return pytesseract.image_to_string(images[0])
            return ""
        except Exception as e:
            logger.warning(f"OCR failed for page {page_number}: {str(e)}")
            return ""

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX files."""
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise FileProcessingError(f"DOCX extraction failed: {str(e)}")

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text."""
        text = text.lower()
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\.+', '.', text)
        return text.strip()

# Other utility classes (FileManager, CacheManager, TextAnalyzer, MetricsCollector, TextSummarizer) remain unchanged.

# Initialize global instances
text_extractor = TextExtractor()
file_manager = FileManager(upload_folder='uploads')
cache_manager = CacheManager()
metrics_collector = MetricsCollector()

def validate_file(file, max_size: int = FileHandler.MAX_FILE_SIZE) -> bool:
    """Validate file before processing."""
    if not file:
        return False
    
    filename = file.filename
    file_size = file.content_length if hasattr(file, 'content_length') else 0

    return (
        '.' in filename and
        os.path.splitext(filename)[1].lower() in FileHandler.ALLOWED_EXTENSIONS and
        file_size <= max_size
    )

def setup_logging(log_file: str = 'file_processing.log'):
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

setup_logging()

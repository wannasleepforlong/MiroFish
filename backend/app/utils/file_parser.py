"""
File parsing utilities.

Supports text extraction from PDF, Markdown, and TXT files.
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional


def _read_text_with_fallback(file_path: str) -> str:
    """
    Read a text file, automatically detecting encoding if UTF-8 fails.

    Strategy:
    1. Try UTF-8 decode first.
    2. Use charset_normalizer to detect encoding.
    3. Fall back to chardet.
    4. Finally default to UTF-8 with errors='replace'.

    Args:
        file_path: File path.

    Returns:
        Decoded text content.
    """
    data = Path(file_path).read_bytes()
    
    # First, try UTF-8
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        pass
    
    # Try charset_normalizer to detect encoding
    encoding = None
    try:
        from charset_normalizer import from_bytes
        best = from_bytes(data).best()
        if best and best.encoding:
            encoding = best.encoding
    except Exception:
        pass
    
    # Fall back to chardet
    if not encoding:
        try:
            import chardet
            result = chardet.detect(data)
            encoding = result.get('encoding') if result else None
        except Exception:
            pass
    
    # Final fallback: UTF-8 + replace
    if not encoding:
        encoding = 'utf-8'
    
    return data.decode(encoding, errors='replace')


class FileParser:
    """High-level file parser."""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.md', '.markdown', '.txt', '.xml'}
    
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """
        Extract plain text from a file.

        Args:
            file_path: Path to the file.

        Returns:
            Extracted text content.
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {suffix}")
        
        if suffix == '.pdf':
            return cls._extract_from_pdf(file_path)
        elif suffix in {'.md', '.markdown'}:
            return cls._extract_from_md(file_path)
        elif suffix == '.txt':
            return cls._extract_from_txt(file_path)
        elif suffix == '.xml':
            return cls._extract_from_xml(file_path)

        raise ValueError(f"Unhandled file extension: {suffix}")
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Tries Mistral OCR first for best quality markdown output.
        Falls back to PyMuPDF if Mistral fails (no API key, network error, etc.)
        """
        from ..utils.logger import get_logger
        logger = get_logger('mirofish.file_parser')
        
        # Try Mistral OCR first for better quality
        try:
            result = FileParser._extract_from_pdf_mistral(file_path)
            logger.info("PDF extracted using Mistral OCR (high quality markdown)")
            # Mistral succeeded - return result
            return result
        except Exception as e:
            logger.warning(f"Mistral OCR failed, falling back to PyMuPDF: {e}")
        
        # Fall back to PyMuPDF
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF is required: pip install PyMuPDF")
        
        logger.info("PDF extracted using PyMuPDF (fallback mode)")
        
        text_parts = []
        with fitz.open(file_path) as doc:
            for page in doc:
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    def _extract_from_pdf_mistral(file_path: str) -> str:
        """
        Extract text from PDF using Mistral OCR API.
        Returns markdown-formatted text for better quality.
        
        Raises:
            ImportError: If mistralai package not installed
            ValueError: If API key not configured
            Exception: If API call fails
        """
        try:
            # Try v2.x import first (mistralai>=2.0.0)
            from mistralai.client import Mistral
        except ImportError:
            try:
                # Fall back to v1.x import (mistralai<2.0.0)
                from mistralai import Mistral
            except ImportError:
                raise ImportError("mistralai not installed: pip install mistralai")
        
        # Get API key from environment or config
        api_key = os.environ.get('MISTRAL_API_KEY', '')
        if not api_key:
            # Try to read from .env file in project root
            # file_parser.py is at E:/MiroFish/backend/app/utils/file_parser.py
            # .env is at E:/MiroFish/.env
            env_path = "E:/MiroFish/.env"
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('MISTRAL_API_KEY'):
                            if '=' in line:
                                parts = line.split('=', 1)
                                if len(parts) > 1:
                                    api_key = parts[1].strip().strip('"').strip("'").strip()
                                    break
        
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not configured")
        
        client = Mistral(api_key=api_key)
        
        # Upload file - use correct API for mistralai version
        with open(file_path, "rb") as f:
            uploaded = client.files.upload(
                file={"file_name": os.path.basename(file_path), "content": f},
                purpose="ocr"
            )
        
        # Get signed URL
        signed_url = client.files.get_signed_url(file_id=uploaded.id)
        
        # Process with OCR
        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "document_url", "document_url": signed_url.url}
        )
        
        # Extract markdown from all pages
        pages_md = []
        for page in response.pages:
            pages_md.append(page.markdown)
        
        return "\n\n".join(pages_md)
    
    @staticmethod
    def _extract_from_md(file_path: str) -> str:
        """Extract text from a Markdown file (with automatic encoding detection)."""
        return _read_text_with_fallback(file_path)
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Extract text from a TXT file (with automatic encoding detection)."""
        return _read_text_with_fallback(file_path)

    @staticmethod
    def _extract_from_xml(file_path: str) -> str:
        """
        Extract text from XML file using streaming parser.
        Automatically detects MediaWiki/Wikipedia dump format.
        For generic XML, recursively extracts all text content.
        """
        is_mediawiki = False
        try:
            for event, elem in ET.iterparse(file_path, events=('start',)):
                local_tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                if local_tag == 'mediawiki':
                    is_mediawiki = True
                break
        except ET.ParseError:
            pass

        if is_mediawiki:
            return FileParser._extract_mediawiki_xml(file_path)
        else:
            return FileParser._extract_generic_xml(file_path)

    @staticmethod
    def _extract_mediawiki_xml(file_path: str) -> str:
        """
        Stream-parse Wikipedia/MediaWiki XML dump.
        Extract article titles and content, suitable for 1GB+ files.
        """
        parts = []
        current_title = None

        for event, elem in ET.iterparse(file_path, events=('end',)):
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

            if tag == 'title':
                current_title = (elem.text or '').strip()
            elif tag == 'text':
                raw = (elem.text or '').strip()
                if current_title and raw:
                    parts.append(f"=== {current_title} ===\n{raw}")
                elem.clear()
            elif tag == 'page':
                current_title = None
                elem.clear()

        return "\n\n".join(parts)

    @staticmethod
    def _extract_generic_xml(file_path: str) -> str:
        """
        Parse generic XML file, recursively extract all text node content.
        """
        try:
            tree = ET.parse(file_path)
        except ET.ParseError as e:
            raise ValueError(f"XML parsing failed: {e}")

        parts = []

        def collect_text(elem):
            text = (elem.text or '').strip()
            tail = (elem.tail or '').strip()
            if text:
                parts.append(text)
            for child in elem:
                collect_text(child)
            if tail:
                parts.append(tail)

        collect_text(tree.getroot())
        return "\n".join(parts)

    @classmethod
    def extract_from_multiple(cls, file_paths: List[str]) -> str:
        """
        Extract and concatenate text from multiple files.

        Args:
            file_paths: List of file paths.

        Returns:
            Combined text from all files.
        """
        all_texts = []
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                text = cls.extract_text(file_path)
                filename = Path(file_path).name
                all_texts.append(f"=== Document {i}: {filename} ===\n{text}")
            except Exception as e:
                all_texts.append(f"=== Document {i}: {file_path} (extraction failed: {str(e)}) ===")
        
        return "\n\n".join(all_texts)


def split_text_into_chunks(
    text: str, 
    chunk_size: int = 500, 
    overlap: int = 50
) -> List[str]:
    """
    Split a long text into overlapping chunks.

    Args:
        text: Original text.
        chunk_size: Target number of characters per chunk.
        overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to split at sentence boundaries
        if end < len(text):
            # Look for the nearest sentence terminator
            for sep in ['。', '！', '？', '.\n', '!\n', '?\n', '\n\n', '. ', '! ', '? ']:
                last_sep = text[start:end].rfind(sep)
                if last_sep != -1 and last_sep > chunk_size * 0.3:
                    end = start + last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Next chunk starts from the overlap position
        start = end - overlap if end < len(text) else len(text)
    
    return chunks


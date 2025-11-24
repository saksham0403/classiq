"""
OCR Service for extracting text from images and PDFs.
Supports EasyOCR (preferred) and Tesseract as fallback.
"""
import os
import tempfile
from typing import Optional
from pathlib import Path

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


async def extract_text_from_file(file_path: str) -> str:
    """
    Uses EasyOCR (preferred) or Tesseract to extract text from an image/PDF.
    Returns a single cleaned text block.
    """
    file_ext = Path(file_path).suffix.lower()
    
    # Handle PDFs
    if file_ext == '.pdf':
        return await _extract_from_pdf(file_path)
    
    # Handle images
    elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
        return await _extract_from_image(file_path)
    
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")


async def _extract_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    all_text = []
    
    # Try PyMuPDF first (faster, better text extraction)
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text:
                    all_text.append(text)
            doc.close()
            return "\n".join(all_text)
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}, trying pdf2image...")
    
    # Fallback: Convert PDF pages to images and OCR
    if PDF2IMAGE_AVAILABLE:
        try:
            images = convert_from_path(file_path)
            for img in images:
                # Save temp image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    img.save(tmp.name)
                    text = await _extract_from_image(tmp.name)
                    all_text.append(text)
                    os.unlink(tmp.name)
            return "\n".join(all_text)
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {e}")
    
    raise ValueError("No PDF extraction library available. Install PyMuPDF or pdf2image.")


async def _extract_from_image(file_path: str) -> str:
    """Extract text from image file."""
    # Try EasyOCR first (better accuracy)
    if EASYOCR_AVAILABLE:
        try:
            reader = easyocr.Reader(['en'], gpu=False)  # Use CPU for compatibility
            results = reader.readtext(file_path)
            # Combine all detected text
            text_lines = [result[1] for result in results]
            return "\n".join(text_lines)
        except Exception as e:
            print(f"EasyOCR extraction failed: {e}, trying Tesseract...")
    
    # Fallback to Tesseract
    if TESSERACT_AVAILABLE:
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise ValueError(f"Tesseract extraction failed: {e}")
    
    raise ValueError("No OCR library available. Install easyocr or pytesseract.")


def clean_ocr_text(text: str) -> str:
    """
    Lightly clean OCR text:
    - Remove excessive whitespace
    - Normalize line breaks
    - Remove common OCR artifacts
    """
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]  # Remove empty lines
    
    # Join with single newlines
    cleaned = '\n'.join(lines)
    
    # Remove common OCR artifacts (very light cleaning)
    cleaned = cleaned.replace('|', 'l')  # Common OCR mistake
    cleaned = cleaned.replace('0', 'O')  # Only if context suggests it
    
    return cleaned


import pytesseract
import fitz  
from PIL import Image
import io
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF using PyMuPDF + Tesseract OCR.
    Works without Poppler.
    """
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        pix = page.get_pixmap(dpi=300)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        text += pytesseract.image_to_string(img)
    
    return text


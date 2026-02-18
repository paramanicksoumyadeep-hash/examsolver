import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import io

# Path to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF using PyMuPDF + Tesseract OCR.
    Works without Poppler.
    """
    # Open the PDF
    doc = fitz.open(pdf_path)
    text = ""

    # Loop through each page
    for page in doc:
        # Render page to an image (pixmap)
        pix = page.get_pixmap(dpi=300)
        
        # Convert pixmap to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # OCR the image
        text += pytesseract.image_to_string(img)
    
    return text


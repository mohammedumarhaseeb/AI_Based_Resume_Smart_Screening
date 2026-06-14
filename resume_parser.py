import os
import re
from PyPDF2 import PdfReader
import docx
try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

def extract_text_from_pdf(filepath):
    text = ""
    try:
        reader = PdfReader(filepath)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(filepath):
    text = ""
    try:
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def extract_text_from_image(filepath):
    """OCR for images."""
    if not pytesseract or not Image:
        return "OCR Libraries not installed. Please check requirements.txt"
    try:
        return pytesseract.image_to_string(Image.open(filepath))
    except Exception as e:
        print(f"Error reading Image: {e}")
        return ""

def extract_text(filepath):
    """Routing function based on file extension."""
    ext = filepath.lower()
    if ext.endswith('.pdf'):
        return extract_text_from_pdf(filepath)
    elif ext.endswith('.docx'):
        return extract_text_from_docx(filepath)
    elif ext.endswith(('.png', '.jpg', '.jpeg')):
        return extract_text_from_image(filepath)
    else:
        return ""

def extract_name(text):
    """
    Very simple heuristic to extract a name.
    Assuming the name is usually at the top of the resume.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return "Unknown Candidate"
    # Return the first line with alphabetic characters as the presumed name
    for line in lines[:5]:
        if len(line) > 2 and len(line) < 40 and any(c.isalpha() for c in line):
            # Strip out generic words if the format is bad
            if "resume" not in line.lower() and "cv" not in line.lower() and "curriculum vitae" not in line.lower():
                return line
    return "Unknown Candidate"

def extract_contact_info(text):
    """Extracts email, phone number, and address using regex and heuristics."""
    email = "Not Found"
    phone = "Not Found"
    address = "Address unavailable from resume"
    
    # Regex for email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        email = email_match.group(0)
        
    # Regex for phone number
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if phone_match:
        phone = phone_match.group(0)
        
    # Heuristic for Address
    # We'll look in the first 800 characters where contact info usually resides
    header = text[:800]
    
    # Pattern 1: Street Address formats
    address_patterns = [
        r'\d+\s+[\w\s]{3,}(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Court|Ct|Circle|Cir|Zip|Parkway|Pkwy|Boulevard|Blvd|Way|Square|Plaza)',
        r'[A-Z][a-z]+,\s*[A-Z]{2}\s*\d{5}', # City, ST 12345
        r'[A-Z][a-z]+,\s*[A-Z][a-z]+',       # City, Country or City, State
        r'Location:\s*[\w\s,]+',             # Location: New York, NY
        r'Address:\s*[\w\s,]+'               # Address: 123 Main St
    ]
    
    for pattern in address_patterns:
        match = re.search(pattern, header, re.IGNORECASE)
        if match:
            address = match.group(0).replace("Location:", "").replace("Address:", "").strip()
            break

    return {"email": email, "phone": phone, "address": address}

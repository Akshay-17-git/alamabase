import pdfplumber
import re

def parse_questionnaire(uploaded_file) -> list[dict]:
    """
    Extract numbered questions from uploaded PDF questionnaire.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        List of dictionaries with 'number' and 'question' keys
    """
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Match patterns like "1." or "1)" at start of line
    # Also handles "Question 1:" format
    patterns = [
        r'(?m)^(\d+)[.)]\s+(.+?)(?=\n\d+[.)]|\Z)',  # 1. or 1) format
        r'(?m)^Question\s+(\d+)[:\.]?\s+(.+?)(?=\nQuestion\s+\d+|\Z)',  # Question 1: format
    ]
    
    questions = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            for num, question_text in matches:
                questions.append({
                    "number": int(num),
                    "question": question_text.strip().replace("\n", " ")
                })
            break
    
    # Sort by question number and remove duplicates
    questions = sorted(questions, key=lambda x: x["number"])
    
    # Remove duplicates (keep first occurrence)
    seen = set()
    unique_questions = []
    for q in questions:
        if q["number"] not in seen:
            seen.add(q["number"])
            unique_questions.append(q)
    
    return unique_questions


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Extracted text as string
    """
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_txt(uploaded_file) -> str:
    """
    Extract text from a TXT file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        File content as string
    """
    return uploaded_file.read().decode("utf-8")


def extract_text_from_docx(uploaded_file) -> str:
    """
    Extract text from a DOCX file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Extracted text as string
    """
    try:
        from docx import Document
        doc = Document(uploaded_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Error reading DOCX file: {str(e)}")


def detect_file_type(filename: str) -> str:
    """
    Detect file type from filename extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        File type: 'pdf', 'txt', 'docx', or 'unknown'
    """
    if filename.endswith('.pdf'):
        return 'pdf'
    elif filename.endswith('.txt'):
        return 'txt'
    elif filename.endswith('.docx'):
        return 'docx'
    else:
        return 'unknown'


def extract_text(uploaded_file) -> str:
    """
    Extract text from any supported file type.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Extracted text as string
    """
    filename = uploaded_file.name
    file_type = detect_file_type(filename)
    
    if file_type == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_type == 'txt':
        return extract_text_from_txt(uploaded_file)
    elif file_type == 'docx':
        return extract_text_from_docx(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

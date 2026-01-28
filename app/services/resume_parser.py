import pdfplumber
import docx
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    # ⚠ wrap bytes in BytesIO
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore').strip()



def extract_text_from_docx(file_bytes: bytes) -> str:
    file_stream = io.BytesIO(file_bytes)
    doc = docx.Document(file_stream)
    text= "\n".join([para.text for para in doc.paragraphs])
    return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore').strip()

def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type. Upload PDF or DOCX only.")


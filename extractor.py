import pymupdf
from docx import Document

def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    try:
        with pymupdf.open(pdf_path) as file:
            for page in file:
                extracted_text += page.get_text()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return extracted_text

def extract_text_from_docx(docx_path):
    extracted_text = ""
    try:
        document = Document(docx_path)
        for paragraph in document.paragraphs:
            extracted_text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
    return extracted_text


pdf_text = extract_text_from_pdf("resume-sample.pdf")
docx_text = extract_text_from_docx("resume-sample.docx")

print(pdf_text)
print(docx_text)

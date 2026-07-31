from pathlib import Path

from pypdf import PdfReader
from docx import Document


def read_pdf(file_path: str) -> str:
    """
    Extract text from PDF resume.
    """

    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text



def read_docx(file_path: str) -> str:
    """
    Extract text from DOCX resume.
    """

    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)



def read_resume(file_path: str) -> str:
    """
    Detect file type and extract resume text.
    """

    path = Path(file_path)

    extension = path.suffix.lower()


    if extension == ".pdf":

        return read_pdf(file_path)


    elif extension == ".docx":

        return read_docx(file_path)


    else:

        raise ValueError(
            "Only PDF and DOCX files are supported."
        )

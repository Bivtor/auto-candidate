from pydantic import BaseModel
from typing import Optional
import PyPDF2
import docx
import pathlib
import logging

LOGGER_PATH = 'receipt.log'
GROUP_ID = 'new_group36573__1'  # Default to Candidates Group

ENV_PATH = '../../.env'
CM_PATH = '/Users/victorrinaldi/Desktop/projects/auto_candidate/json_files/cm.csv'
CANDIDATE_CSV_PATH = '/Users/victorrinaldi/Desktop/projects/auto_candidate/scripts/jobdiva_monday/csvs/candidate.csv'
CANDIDATE_NOTES_CSV_PATH = 'csvs/candidatenote.csv'
RESUME_CSV_PATH = 'csvs/resume.csv'
RESUME_FOLDER_PATH = '/Volumes/T7/sbt_files/unzip/resumes/'
RECRUITERS_CSV_PATH = 'csvs/recruiter.csv'
ENV_PATH = '../../.env'


# Logging formation
logger = logging.getLogger('logger')

# Set logger level
logger.setLevel(logging.DEBUG)

# create handler
handler = logging.FileHandler(LOGGER_PATH)

# set handler level
handler.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# set formatter
handler.setFormatter(formatter)

# add handler to logger
logger.addHandler(handler)


def get_raw_text(file_path: str) -> str:
    """
    Extracts raw text from a document file. Supports .docx, .pdf, and .rtf formats.

    Args:
        file_path (str): The path to the document file.

    Returns:
        str: The extracted text from the document.

    Raises:
        ValueError: If the file format is unsupported.

    Notes:
        - For .docx files, extracts text from paragraphs.
        - For .pdf files, extracts text from all pages.
        - For .rtf files, converts the RTF format to pdf.
    """
    # Define text string and get file extension
    text = ""
    file_extension = pathlib.Path(file_path).suffix.lower().strip()
    # print(file_extension)
    # If .docx file
    if file_extension == '.docx':
        # Load the .docx file and join paragraphs
        doc = docx.Document(file_path)
        text = ' '.join([para.text for para in doc.paragraphs])

    # If .pdf file
    elif file_extension == '.pdf':
        with open(file_path, 'rb') as f:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(f)

            # Get the number of pages in the PDF file
            num_pages = len(pdf_reader.pages)

            # Loop through all the pages and extract the text
            for page in range(num_pages):
                # Get the page object
                pdf_page = pdf_reader.pages[page]
                # Extract the text from the page
                page_text = pdf_page.extract_text()
                if page_text:
                    text += page_text

    # If .rtf file
    elif file_extension == '.rtf':
        with open(file_path, 'rb') as f:
            # Parse the .rtf content
            text = file_path.read()

    # Unsupported file format
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    return text


class CandidateData(BaseModel):
    hasResume: Optional[bool] = None
    location: Optional[str] = None
    GPS_COORD: Optional[dict] = {'lat': ' ', 'long': ' '}
    LA_area: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    date: Optional[str] = None
    pagelink: Optional[str] = None
    source: Optional[str] = "JobDiva Import"
    license_cert: Optional[str] = None
    license_expiration: Optional[str] = None
    title: Optional[str] = None
    monday_id: Optional[str] = None
    notes_id: Optional[str] = None
    jobdiva_notes: Optional[str] = None
    hasNotes: Optional[bool] = None
    resume_file: Optional[str] = None
    jobdiva_id: Optional[str] = None
    occupation_title: Optional[str] = None
    occupation_id: Optional[int] = None

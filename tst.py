from pydantic import BaseModel
import PyPDF2
import re
import os
import glob

from auto_candidate import *


class candidateData(BaseModel):
    hasResume: bool | None
    location: str
    name: str
    phone: str
    email: str
    date: str
    pagelink: str
    source: str


def parse_resume2(data: candidateData):
    # Only do this for Indeed when a resume is present
    if data.source != "Indeed" or (not data.hasResume):
        return

    # Get the directory of target file (Latest in folder )
    list_of_files = glob.glob("N:\Downloads2\*.pdf")  # PC Dir

    # PC Dir
    # directory = max(list_of_files, key=os.path.getctime)

    # Mac Dir
    directory = '/Users/victorrinaldi/Desktop/auto_candidate/resumes/ResumeRobert-AlnieGarlit.pdf'

    # Define regex Patterns
    phone_regex = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    email_regex = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    # Open the PDF file in read-binary mode
    with open(directory, 'rb') as f:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(f)

        # Get the number of pages in the PDF file
        num_pages = len(pdf_reader.pages)

        # Loop through all the pages and extract the text
        text = ''
        for page in range(num_pages):
            # Get the page object
            pdf_page = pdf_reader.pages[page]
            # Extract the text from the page
            page_text = pdf_page.extract_text()
            # Add the page text to the overall text variable
            text += page_text

        # Use regular expressions to find phone numbers and emails in the text
        data.phone = phone_regex.findall(text)[0]
        data.email = email_regex.findall(text)[0]

        # Print the results for the current PDF file
    print("Altered Phone/Email for Indeed Candidate with Resume")


def main():
    d = candidateData(hasResume=True, location="Florida", name="Robert", phone="8057227847",
                      email="kk20@gmail.com", date="10/10/2020", pagelink="nack", source="Indeed")

    d2 = candidateData(hasResume=True, location="Cali", name="Jonathan", phone="8057227847",
                       email="johnwick@gmail.com", date="10/10/2020", pagelink="nack", source="Indeed")
    parse_resume(d2)
    parse_resume(d)

    print(d2, "\n")
    print(d, "\n")


if __name__ == "__main__":
    main()

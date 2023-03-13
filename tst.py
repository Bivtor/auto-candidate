from pydantic import BaseModel
import PyPDF2
import re
import os
import glob
from fuzzywuzzy import fuzz
from auto_candidate import *


def parse_resume2(data: candidateData, directory: str):
    # Only do this for Indeed when a resume is present
    if data.source != "Indeed" or (not data.hasResume):
        return

    # Get the directory of target file (Latest in folder )
    list_of_files = glob.glob("N:\Downloads2\*.pdf")  # PC Dir

    # PC Dir
    # directory = max(list_of_files, key=os.path.getctime)

    # Mac Dir
    # directory = '/Users/victorrinaldi/Desktop/auto_candidate/resumes/Janine Hernandez Nurse (Los Angeles, CA).pdf'

    # Define regex Patterns
    phone_regex = re.compile(r"\(?\d{3}\)?[-.\s]*?\d{3}[-.\s]*?\d{4}")
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

        newPhone = phone_regex.findall(text)
        newEmail = email_regex.findall(text)

        print(newPhone)
        print(newEmail)

        if len(newPhone) > 0:
            data.phone = newPhone[0]
        if len(newEmail) > 0:
            data.email = newEmail[0]

        # Print the results for the current PDF file
    print("Altered Phone/Email for: {} in directory: {}".format(data.name, directory))


def main():
    # x = getLicenseInfo("Dane Miller", 5)
    # spreadsheet_appends = curateLicenseList(x)

    build_request("lsit", "sds")


# +1(562) 395 -2587


def test_regex(text):
    # Define regex Patterns
    phone_regex = re.compile(r"\(?\d{3}\)?[-.\s]*?\d{3}[-.\s]*?\d{4}")

    return phone_regex.findall(text)


def build_request(info, licenselist2):
    requestdata = {
        'requests': [
            {
                "appendCells":
                {
                    "sheetId": "11123",
                    "rows": [{
                        "values": [
                            {"userEnteredValue": {
                                "formulaValue": "=HYPERLINK(\"{}\",\"{}\")".format("folder_link", info[0])}},
                            {"userEnteredValue": {
                                "formulaValue": "=HYPERLINK(\"{}\",\"{}\")".format(info[7], info[1])}},
                            {"userEnteredValue": {"stringValue": info[2]}},
                            {"userEnteredValue": {"stringValue": info[3]}},
                            {"userEnteredValue": {"stringValue": info[4]}},
                            {"userEnteredValue": {"stringValue": info[5]}},

                            # License portion
                            {"userEnteredValue": {
                                "stringValue": licenselist2[0]}},
                            {"userEnteredValue": {
                                "stringValue": licenselist2[1]}},
                            {"userEnteredValue": {
                                "stringValue": licenselist2[2]}},
                            {"userEnteredValue": {
                                "stringValue": licenselist2[3]}},
                            {"userEnteredValue": {
                                "stringValue": licenselist2[4]}}
                        ]}],
                    "fields": "userEnteredValue"
                }
            }
        ]
    }


if __name__ == "__main__":
    main()

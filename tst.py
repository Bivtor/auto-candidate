
import sys
import os
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from pydantic import BaseModel
import json
import os.path
from auto_candidate import *


def publish():
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    if os.path.exists('credls/token.json'):
        creds = Credentials.from_authorized_user_file(
            'creds/token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds/credentials2.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('creds/token.json', 'w') as token:
            token.write(creds.to_json())

    # Try
    try:
        gmail = build('gmail', 'v1', credentials=creds)
        request = {
            'labelIds': ['INBOX', 'SPAM'],
            'topicName': 'projects/auto-candidate-365121/topics/my_topic'
        }
        response = gmail.users().watch(userId='me', body=request).execute()
        print(response)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def test_regex(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Find name in raw text
        raw_message = file.read()
        loc = raw_message.find("New Candidate:")
        candidate_name = raw_message[loc+15:loc+100]
        candidate_name = candidate_name[:candidate_name.find("for")].strip()
        print(candidate_name)

        # Find job title in text
        loc = raw_message.find("for '")
        job_title = raw_message[loc+5: loc+100]
        job_title = job_title[:job_title.find("'")].lower().strip()
        print(job_title)

        with open('name_map.json') as f:
            name_map: dict = json.load(f)

            # If the job_title exists in our map of titles
            if job_title in name_map:

                # Deterine which category the candidate should be added to
                sheet_destination = name_map[job_title]

                # Get entire column 1 (names column)
                names_list = get_names(
                    spreadsheet_id='1c21ffEP_x-zzUKrxHhiprke724n9mEdY805Z2MphfXU', sheet_name=sheet_destination)

                # Check if the candidate name is already in the spreadsheet
                if candidate_name in names_list:
                    print("Candidate already in database")
                    return 200

                # If Candidate NOT in spreadsheet -> Add the Candidate to the spreadsheet
                candidate_url = ""  # TODO Remove this

                # Call clone of submit data (checks password, isRunning, columnVariables, etc)

                can_data = Data(action='Add', category=sheet_destination,
                                link=candidate_url, password='gabeandcara2023', message="")

                print("Adding Candidate...")
                # submitdata_clone(data=can_data)

                # TODO Get the last line of the spreadsheet
                # TODO Call the send text function for only the last line of the spreadsheet
            else:
                print("Could not find job type -> google sheet association")


def add_mail_candidate(url: str):

    d = Data()


def get_spreadsheet_names(sheet_id, sheet_name):
    pass


class MailData(BaseModel):
    message: dict


def converttotxt(fp):
    with open(fp, 'rb') as f:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(f)

        # Get the number of pages in the PDF file
        num_pages = len(pdf_reader.pages)

        text = ''
        # Loop through all the pages and extract the text
        for page in range(num_pages):
            # Get the page object
            pdf_page = pdf_reader.pages[page]
            # Extract the text from the page
            page_text = pdf_page.extract_text()
            # Add the page text to the overall text variable
            text += page_text

        # Open a new text file in write mode
        txt_file = open('resume_output.txt', 'w')

        # Write the extracted text to the text file
        txt_file.write(text)

        # Close the text file
        txt_file.close()


def main():
    # publish()
    converttotxt('resume.pdf')
    # get_spreadsheet_names(SPREADSHEET_ID, "Therapist")
    # test_regex("/Users/victorrinaldi/Desktop/auto_candidate/test.txt")


if __name__ == "__main__":
    main()

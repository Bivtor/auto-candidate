from twilio.rest import Client
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import date, datetime
from fuzzywuzzy import fuzz

import pathlib
import docx
import time
import PyPDF2
import os
import os.path
import json
import glob
import re
from bs4 import BeautifulSoup

import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Amazon SES Send Email info
import boto3
import logging

# import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

logger = logging.getLogger(__name__)
load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/documents',
          'https://www.googleapis.com/auth/spreadsheets']

"""
Creates Credentials to be used globally
"""
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('creds/token.json'):
    creds = Credentials.from_authorized_user_file('creds/token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'creds/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('creds/token.json', 'w') as token:
        token.write(creds.to_json())

# Gabe Sheet ID
SPREADSHEET_ID = '1c21ffEP_x-zzUKrxHhiprke724n9mEdY805Z2MphfXU'


class Data(BaseModel):
    password: str
    action: str
    category: str
    link: str = ""
    start: int = 2
    end: int = 1000
    message: str = ""
    messageType: str = ""

    # Sheet/Folder containment info
    isSheet: bool = False
    isFolder: bool = False
    sheetId: str | None = None
    folderId: str | None = None

    # Sheet position info
    positions: list[str] = []
    err: str | None = None


class candidateData(BaseModel):
    hasResume: bool | None
    location: str
    name: str
    phone: str
    email: str
    date: str
    pagelink: str
    source: str
    license_cert: str | None
    license_expiration: str | None


class License(BaseModel):
    name: str
    type: str
    number: str
    expiration: str
    location: str


def upload_basic(title, parents, path):
    """Insert new file.
    Returns : Id's of the file uploaded

    Load pre-authorized user credentials from the environment.
    for guides on implementing OAuth2 for the application.
    """

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': title, 'parents': parents}

        # Determine if file is pdf or docx and set media accoordingly
        file_extension = pathlib.Path(path).suffix.strip()
        media = media = MediaFileUpload(
            path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document') if file_extension == ".docx" else MediaFileUpload(
            path, mimetype='application/pdf')

        # Execute upload
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File ID: {file.get("id")}')
        print("Uploaded Resume Successfully")
        return file.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None


def update_spreadsheet(candidateData: candidateData, data, SPREADSHEET_ID, SHEET_ID, folder_link):
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Base Request data format
        requestdata = {
            'requests': [
                {
                    "appendCells":
                    {
                        "sheetId": SHEET_ID,
                        "rows": [{
                            "values": [
                            ]}],
                        "fields": "userEnteredValue"
                    }
                }
            ]
        }

        # Build request data form dynamically to account for changes in column order
        # Column names must be exact however

        for value in data['positions']:
            # Define new dict (Cell + data to add)
            new_dict = dict()

            # Match value to a case
            match value:
                case "Name":
                    new_dict = {"userEnteredValue": {
                        "formulaValue": "=HYPERLINK(\"{}\",\"{}\")".format(folder_link, candidateData.name)}}
                case "Source":
                    new_dict = {"userEnteredValue": {
                        "formulaValue": "=HYPERLINK(\"{}\",\"{}\")".format(candidateData.pagelink, candidateData.source)}}
                case "Location":
                    new_dict = {"userEnteredValue": {
                        "stringValue": candidateData.location}}
                case "Phone":
                    new_dict = {"userEnteredValue": {
                        "stringValue": candidateData.phone}}
                case "Email":
                    new_dict = {"userEnteredValue": {
                        "stringValue": candidateData.email}}
                case "Date Applied":
                    new_dict = {"userEnteredValue": {
                        "stringValue": candidateData.date}}
                case "License/Cert":
                    new_dict = {"userEnteredValue": {
                        "stringValue": candidateData.license_cert}}
                case "L Expiration":
                    new_dict = {"userEnteredValue": {
                        "stringValue": candidateData.license_expiration}}

                # If the item is not one of these things, do not append anything
                case _:
                    continue

            # Add the corresponding dictionary to the request body
            requestdata['requests'][0]['appendCells']['rows'][0]['values'].append(
                new_dict)

        # Execute Batch Update Request
        request = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                                     body=requestdata)
        response = request.execute()
        print("Updated Spreadsheet")

    except HttpError as err:
        print(err)


def create_file_general(data, parents, title):
    # create file
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'mimeType': 'application/vnd.google-apps.document',
            'name': title,
            'parents': parents
        }
        file = service.files().create(body=file_metadata, fields='id',
                                      ).execute()
        print(F'Document was created with ID: "{file.get("id")}".')

        ###########################################
        inputName = "Name: " + data.name + "\n"
        inputPhone = "Phone: " + data.phone + "\n"
        inputEmail = "Email: " + data.email + "\n"
        inputDate = "Date Applied: " + data.date + "\n"
        inputLocation = "Location: " + data.location + "\n"
        restOfQuestions = ("Willingness to commute to?:\n",
                           "Yrs Exp w / Treatment?:\n",
                           "\t- If so, where?:\n",
                           "Yrs Exp w / Kipu?:\n",
                           "\t- If not, tech savvy?:\n",
                           "\t- Doctors Orders?:\n",
                           "\t- COWS/CIWA?:\n",
                           "FT/PT/Per Diem?:\n"
                           "When Start?:\n",
                           "Desired Hours?:\n",
                           "Desired Wage?:\n",
                           "Availability?:\n",
                           "Open to nights?:\n",
                           "Med Destruction?:\n",
                           "Licenses and certs?:\n",
                           "\t- Verified?:\n",
                           "Active CPR/FA?:\n",
                           "Other Notes?:\n\n\n")
        bigString = ""
        for items in restOfQuestions:
            bigString += items
        ###########################################

        # update said file with the items scraped from source
        try:
            service2 = build('docs', 'v1', credentials=creds)
            DOCUMENT_ID = file.get('id')

            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': "INTERVIEW QUESTIONS\n"
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': 21,
                        },
                        'text': inputName,
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputName)+21,
                        },
                        'text': inputPhone
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+21,
                        },
                        'text': inputEmail
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+21 + len(inputEmail)
                        },
                        'text': inputDate
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+21 + len(inputEmail) + len(inputDate)
                        },
                        'text': inputLocation
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+21 + len(inputEmail) + len(inputDate) + len(inputLocation)
                        },
                        'text': bigString
                    }
                },
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex':  21
                        },
                        'textStyle': {
                            'bold': True,
                        },
                        "fields": "bold"  # Added
                    }
                },
                {
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex':  2
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'NORMAL_TEXT',
                            'alignment': 'CENTER'
                        },
                        'fields': 'namedStyleType, alignment'
                    }
                },
                {
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex':  len(inputPhone) + len(inputName)+21 + len(inputEmail) + len(inputDate) + len(inputLocation) + len(bigString)
                        },
                        'paragraphStyle': {
                            'spaceAbove': {
                                'magnitude': 15.0,
                                'unit': 'PT'
                            },
                            'spaceBelow': {
                                'magnitude': 15.0,
                                'unit': 'PT'
                            }
                        },
                        'fields': 'spaceAbove,spaceBelow'

                    }
                },
            ]

            doc = service2.documents().batchUpdate(
                documentId=DOCUMENT_ID, body={'requests': requests}).execute()

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None
        # pylint: disable=maybe-no-member

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None


def create_file_Therapist(data, parents, title):
    # create file
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'mimeType': 'application/vnd.google-apps.document',
            'name': title,
            'parents': parents
        }
        file = service.files().create(body=file_metadata, fields='id',
                                      ).execute()
        print(F'Document was created with ID: "{file.get("id")}".')

        ###########################################
        inputName = "Name: " + data.name + "\n"
        inputPhone = "Phone: " + data.phone + "\n"
        inputEmail = "Email: " + data.email + "\n"
        inputDate = "Date Applied: " + data.date + "\n"
        inputLocation = "Location: " + data.location + "\n"
        restOfQuestions = ("Willingness to commute to?:\n",
                           "Yrs Exp w / Treatment?:\n",
                           "\t- If so, where?:\n",
                           "Yrs Exp w / Kipu?:\n",
                           "\t- If not, tech savvy?:\n",
                           "BPS/Treatment Plans?:\n"
                           "FT/PT/Groups?:\n",
                           "\tWhat kind of groups?:\n",
                           "Telehealth exp?:\n",
                           "Desired Wage?:\n",
                           "Availability?:\n",
                           "CPR/FA?:\n",
                           "Additional Certifications:\n",
                           "General Notes:\n\n\n")
        bigString = ""
        for items in restOfQuestions:
            bigString += items
        ###########################################

        # update said file with the items scraped from source
        try:
            service2 = build('docs', 'v1', credentials=creds)
            DOCUMENT_ID = file.get('id')

            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': "THERAPIST INTERVIEW QUESTIONS\n"
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': 31,
                        },
                        'text': inputName,
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputName)+31,
                        },
                        'text': inputPhone
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+31,
                        },
                        'text': inputEmail
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+31 + len(inputEmail)
                        },
                        'text': inputDate
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+31 + len(inputEmail) + len(inputDate)
                        },
                        'text': inputLocation
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+31 + len(inputEmail) + len(inputDate) + len(inputLocation)
                        },
                        'text': bigString
                    }
                },
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex':  21
                        },
                        'textStyle': {
                            'bold': True,
                        },
                        "fields": "bold"  # Added
                    }
                },
                {
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex':  2
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'NORMAL_TEXT',
                            'alignment': 'CENTER'
                        },
                        'fields': 'namedStyleType, alignment'
                    }
                },
                {
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex':  len(inputPhone) + len(inputName)+21 + len(inputEmail) + len(inputDate) + len(inputLocation) + len(bigString)
                        },
                        'paragraphStyle': {
                            'spaceAbove': {
                                'magnitude': 15.0,
                                'unit': 'PT'
                            },
                            'spaceBelow': {
                                'magnitude': 15.0,
                                'unit': 'PT'
                            }
                        },
                        'fields': 'spaceAbove,spaceBelow'

                    }
                },
            ]

            doc = service2.documents().batchUpdate(
                documentId=DOCUMENT_ID, body={'requests': requests}).execute()

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

        # pylint: disable=maybe-no-member

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None


def create_folder(name: str, parents):
    """ Create a folder and prints the folder ID
    Returns : Folder Id, Folder Share Link
    """

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'mimeType': 'application/vnd.google-apps.folder',
            'name': name,
            'parents': parents
        }
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='*',
                                      ).execute()
        print(
            F'Folder was created with web view link: "{file.get("webViewLink")}"')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return [file.get('id'), file.get('webViewLink')]


def create_candidate(candidateData: candidateData, data):
    """
    Creates a new candidate inside xyz Folder and a new Questions document
    candidateData = candidate information to be inputted
    data = information about columns and sheets
    """

    # Set Proper Variables
    category = data['category']
    title = "{} {} ({})".format(candidateData.name,
                                category, candidateData.location)

    # Clean up Date
    candidateData.date = cleanupdate(candidateData.date, candidateData.source)

    # Fix Phone Number and Email (Indeed Only)
    time.sleep(2)
    parse_resume(candidateData)

    SHEET_ID = data['sheetId']
    parents = [data['folderId']]  # misc default
    print("Parents are: {} for role: {}".format(parents, category))

    # Add id of new parent so that we are inside the proper file
    print("Creating {}'s Folder".format(candidateData.name))
    newParent = create_folder(title, parents)
    folder_id = [newParent[0]]
    folder_link = newParent[1]

    # Create Questions Document
    if category == 'Therapist':
        create_file_Therapist(candidateData, folder_id, title)
    else:
        create_file_general(candidateData, folder_id, title)

    # Get License number of first (depth) entries:
    licenselist = getLicenseInfo(candidateData.name, 5)

    # Add License info if match to candidateData
    curateLicenseList(licenselist, candidateData)

    # Call update spreadsheet function
    update_spreadsheet(candidateData, data, SPREADSHEET_ID,
                       SHEET_ID, newParent[1])

    # Upload the Resume if they had one
    if (candidateData.hasResume):
        # * means all if need specific format then *.csv
        list_of_files = glob.glob("N:\Downloads2\*")
        path = max(list_of_files, key=os.path.getctime)
        upload_basic(title, folder_id, path)
    return [title, folder_id]


def cleanupdate_license(date):
    date2 = ""

    def findMonth(month: str):

        return date[date.find(" ")+1:date.find(",")] + "/" + date[date.find("202")+2:date.find("202")+4]

    if date.find("Jan"):
        date2 += "1/"
        date2 += findMonth("Jan")
    elif date.find("Feb"):
        date2 += "2/"
        date2 += findMonth("Feb")
    elif date.find("Mar"):
        date2 += "3/"
        date2 += findMonth("Mar")
    elif date.find("Apr"):
        date2 += "4/"
        date2 += findMonth("Apr")
    elif date.find("May"):
        date2 += "5/"
        date2 += findMonth("May")
    elif date.find("Jun"):
        date2 += "6/"
        date2 += findMonth("Jun")
    elif date.find("Jul"):
        date2 += "7/"
        date2 += findMonth("Jul")
    elif date.find("Aug"):
        date2 += "8/"
        date2 += findMonth("Aug")
    elif date.find("Sep"):
        date2 += "9/"
        date2 += findMonth("Sep")
    elif date.find("Oct"):
        date2 += "10/"
        date2 += findMonth("Oct")
    elif date.find("Nov"):
        date2 += "11/"
        date2 += findMonth("Nov")
    elif date.find("Dec"):
        date2 += "12/"
        date2 += findMonth("Dec")
    date = date2
    return date


def cleanupdate(date: str, source: str):
    # If the source is ZipRecruiter
    if source == "ZipRecruiter":
        date2: str = ""

        def findMonth(month: str):
            return date[date.find(month)+4:date.find(",")] + "/" + date[date.find("202")+2:date.find("202")+4]
        if date.find("Jan") > 0:
            date2 += "1/"
            date2 += findMonth("Jan")
        elif date.find("Feb") > 0:
            date2 += "2/"
            date2 += findMonth("Feb")
        elif date.find("Mar") > 0:
            date2 += "3/"
            date2 += findMonth("Mar")
        elif date.find("Apr") > 0:
            date2 += "4/"
            date2 += findMonth("Apr")
        elif date.find("May") > 0:
            date2 += "5/"
            date2 += findMonth("May")
        elif date.find("Jun") > 0:
            date2 += "6/"
            date2 += findMonth("Jun")
        elif date.find("Jul") > 0:
            date2 += "7/"
            date2 += findMonth("Jul")
        elif date.find("Aug") > 0:
            date2 += "8/"
            date2 += findMonth("Aug")
        elif date.find("Sep") > 0:
            date2 += "9/"
            date2 += findMonth("Sep")
        elif date.find("Oct") > 0:
            date2 += "10/"
            date2 += findMonth("Oct")
        elif date.find("Nov") > 0:
            date2 += "11/"
            date2 += findMonth("Nov")
        elif date.find("Dec") > 0:
            date2 += "12/"
            date2 += findMonth("Dec")
        date = date2
        return date

    # If the source is indeed do this
    elif source == "Indeed":
        date_obj = datetime.strptime(date, '%b %d, %Y')
        return date_obj.strftime('%m/%d/%Y')


def parse_resume(data: candidateData):

    # Only do this for Indeed when a resume is present
    if data.source != "Indeed" or (not data.hasResume):
        return

    # Get the directory of target file (Latest in folder )

    # PC Dir
    list_of_files = glob.glob("N:\Downloads2\*")
    # Mac Dir (Testing)
    # list_of_files = glob.glob("/Users/victorrinaldi/Desktop/auto_candidate/resumes/*")

    # Target the newest file in the folder
    directory = max(list_of_files, key=os.path.getctime)

    # Define regex Patterns
    phone_regex = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    email_regex = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    # Extract text for pdf or docx
    text = ""
    file_extension = pathlib.Path(directory).suffix.strip()

    # If file type is Docx
    if file_extension == '.docx':
        doc = docx.Document(directory)
        text = '\s'.join([para.text for para in doc.paragraphs])

    else:  # Open the PDF if file type is NON docx
        with open(directory, 'rb') as f:
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
                # Add the page text to the overall text variable
                text += page_text

    # Use regular expressions to find phone numbers and emails in the text
    newPhone = phone_regex.findall(text)
    newEmail = email_regex.findall(text)
    if len(newPhone) > 0:
        data.phone = newPhone[0]
    if len(newEmail) > 0:
        data.email = newEmail[0]

        # Print the results for the current PDF file
    print("Altered Phone/Email for: {} in directory: {}".format(data.name, directory))


def getLicenseInfo(name, depth) -> License:
    # Assign first and last, assuming everything but last word is first name
    first = name[:name.rfind(" ")].strip()
    last = name[name.rfind(" "):].strip()
    url = "https://search.dca.ca.gov/results"
    body = "boardCode=0&licenseType=0&licenseNumber=&firstName={}&lastName={}&registryNumber=".format(
        first, last)
    headers = {
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "if-none-match": 'W/"1e953a-vRUoGgQzuHnWBm/YM/qTtDChpnM"',
        "sec-ch-ua":
            '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            'referrer': "https://search.dca.ca.gov/",
            'referrerPolicy': "strict-origin-when-cross-origin",
            'body': "boardCode=0&licenseType=0&licenseNumber=&firstName=dane&lastName=miller&registryNumber=",
            'method': "POST",
            'mode': "cors",
            'credentials': "include",
    }

    # Collect results
    r = requests.post(url, data=body, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    count = 0
    licenseinfolist = list()

    # For each license we match with, collect the proper data
    for i in soup.find_all('ul', class_="actions"):
        # define items to be collected
        licensetype = ""
        licensenumber = ""
        licenseexpiration = ""
        licenselocation = ""
        if count >= depth:
            break

        # get the s = similarity value from the first li
        name_found = ""
        if i.li.h3:
            name_found = str(i.li.h3.string).lower().strip()
            name_given = (last + ", " + first).lower()
        else:
            continue

        # grab the info from the list items within each profile's ul element
        for j in i.find_all('li'):
            if str(j).find("License Number:") > 0:
                licensenumber = j.a.span.string
            if str(j).find("License Type:") > 0:
                licensetype = j.text[j.text.find(":")+2:]
            if str(j).find("Expiration Date:") > 0:
                licenseexpiration = j.text[j.text.find(":")+2:]
            if str(j).find("City:") > 0:
                licenselocation = str(j.span.text).lower()

         # append license info to return list
        licenseexpiration = cleanupdate_license(licenseexpiration)
        licenseinfolist.append(
            License(name=name_found, type=licensetype, number=licensenumber, expiration=licenseexpiration, location=licenselocation))

        count += 1

    print("Got {} licenses for {}".format(count, name))

    return licenseinfolist


class SesDestination:
    """Contains data about an email destination."""

    def __init__(self, tos, ccs=None, bccs=None):
        """
        :param tos: The list of recipients on the 'To:' line.
        :param ccs: The list of recipients on the 'CC:' line.
        :param bccs: The list of recipients on the 'BCC:' line.
        """
        self.tos = tos
        self.ccs = ccs
        self.bccs = bccs

    def to_service_format(self):
        """
        :return: The destination data in the format expected by Amazon SES.
        """
        svc_format = {'ToAddresses': self.tos}
        if self.ccs is not None:
            svc_format['CcAddresses'] = self.ccs
        if self.bccs is not None:
            svc_format['BccAddresses'] = self.bccs
        return svc_format


class SesMailSender:
    """Encapsulates functions to send emails with Amazon SES."""

    def __init__(self, ses_client):
        """
        :param ses_client: A Boto3 Amazon SES client.
        """
        self.ses_client = ses_client

    def send_email(self, source, destination, subject, text, html, name, category, email, reply_tos=None):
        """
        Sends an email.

        Note: If your account is in the Amazon SES  sandbox, the source and
        destination email accounts must both be verified.

        :param source: The source email account.
        :param destination: The destination email account.
        :param subject: The subject of the email.
        :param text: The plain text version of the body of the email.
        :param html: The HTML version of the body of the email.
        :param reply_tos: Email accounts that will receive a reply if the recipient
                          replies to the message.
        :return: The ID of the message, assigned by Amazon SES.
        """
        send_args = {
            'Source': source,
            'Destination': destination.to_service_format(),
            'Message': {
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': text}}}}
        if reply_tos is not None:
            send_args['ReplyToAddresses'] = reply_tos
        try:
            response = self.ses_client.send_email(**send_args)
            message_id = response['MessageId']
            logger.info(
                "Sent mail %s from %s to %s.", message_id, source, destination.tos)

            write_json({"name": name, "job": category,
                        "email": email, "response_code": response, 'body': text})

            print(
                "Successfully sent email to: {} -> ".format(name, destination.tos[0]))
        except ClientError as err:
            print(
                "Invalid email destination for: {} -> {}".format(name, destination.tos[0]))
            write_json({"name": name, "job": category,
                        "email": email, "response_code": str(err.response)})
        else:
            return message_id


def sendmailtexts(data: Data):
    """
    For loop which decides to or not to send a text and email to the candidate
    the text and email are both call seperate functions which catch errors in formatting
    """

    """"
    Methods for deciding if we should send the text
    """
        # Decide whether or not to send a text/email Function
    def shouldSendMessage(data: Data, values: dict) -> bool:
        if (values[spokenToCol] == 'N' or values[spokenToCol] == ''):
            return True
        else:
            return False
    def shouldSendMessageXs(data: Data, values: dict) -> bool:
        if (values[massText].lower() == 'x' or values[massText] != ''):
            return True
        else:
            return False
        
    try:
        # Create boto3 Client
        client = boto3.client('ses', region_name="us-west-1", aws_access_key_id=os.getenv(
            'aws_access_key_id'), aws_secret_access_key=os.environ.get('aws_secret_access_key'))

        # Create mailsender from boto3 client
        mailsender = SesMailSender(ses_client=client)

        # Create AWS Service
        service = build('sheets', 'v4', credentials=creds)
        print("Attempting to send texts/emails...")
        for row in range(data.start, data.end+1):
            time.sleep(3)  # Wait a little to not use too many requests.
            try:
                # This specifies the Sheet name and which row we re currently working on
                RANGE = "{}!{}:{}".format(
                    data.category, row, row)

                # This uses the range information to get the data from the row of the spreadsheet
                result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                             range=RANGE).execute()
                # Assign data to variable 'Values'
                values = result.get('values', [])[0]

                # Assign column values after changed methods for input
                nameCol = data.positions.index("Name")
                phoneCol = data.positions.index("Phone")
                emailCol = data.positions.index("Email")
                contactedCol = data.positions.index("Contacted")
                timesContactedCol = data.positions.index("Times Contacted")
                spokenToCol = data.positions.index("Spoken To")
                massText = data.positions.index("Mass Text")

                # Find max length of the row insertion we will need
                max_length_row = max(nameCol, phoneCol, emailCol,
                                     contactedCol, timesContactedCol, spokenToCol)+1

                # If the length of the row is not as long as the furthest away category that we need to be inputting into, extend it
                if len(values) < max_length_row:
                    for k in range(len(values), len(values) + max_length_row - len(values)):
                        values.append('')

                # Now we are able to access the proper items in rows before we batch update, because we know they all exist
                name = values[nameCol]
                number = values[phoneCol]
                email = values[emailCol]
                body = data.message.replace(
                    "[candidate_name]", name)  # This was broken before



                # If we decide to send a message
                if shouldSendMessageXs(data, values):

                    # Update the times we have sent a message to this person
                    if values[timesContactedCol] == '':

                        values[timesContactedCol] = '1'
                    else:
                        values[timesContactedCol] = str(
                            int(values[timesContactedCol])+1)

                    # Send a text to the name / phone given
                    sendTwilioText(name=name, number=number,
                                   body=body)

                    # Send an email to the given info
                    sendAWSEmail(name=name, email=email, body=body,
                                 category=data.category, mailsender=mailsender)

                    # Format for updating the cells for times contacted in Google Sheets
                    updatedata = {
                        'requests': [
                            {
                                "updateCells":
                                {
                                    "rows": [
                                        {
                                            "values": [
                                                {
                                                    "userEnteredValue": {"stringValue": values[contactedCol]}
                                                }
                                            ]
                                        }
                                    ],
                                    "fields": 'userEnteredValue',
                                    "start": {
                                        "sheetId": data.sheetId,
                                        "rowIndex": row-1,
                                        "columnIndex": contactedCol
                                    }
                                }
                            },
                            {
                                "updateCells":
                                {
                                    "rows": [
                                        {
                                            "values": [
                                                {
                                                    "userEnteredValue": {"stringValue": values[timesContactedCol]}
                                                }
                                            ]
                                        }
                                    ],
                                    "fields": 'userEnteredValue',
                                    "start": {
                                        "sheetId": data.sheetId,
                                        "rowIndex": row-1,
                                        "columnIndex": timesContactedCol
                                    }
                                }
                            },
                        ]
                    }
                   
                    # Send update
                    request = service.spreadsheets().batchUpdate(
                        spreadsheetId=SPREADSHEET_ID,  body=updatedata).execute()
                else:
                    print("\nChose not to message {}".format(
                        values[nameCol]))
            except IndexError as err:
                print("\nFinished Texting and Emailing Candidaes")
                break
    except HttpError as err:
        print(err)


def sendTwilioText(name: str, number: str, body: str):
    # Find your Account SID and Auth Token and Message
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    service_id = os.environ['TWILIO_SERVICE_ID']

    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            messaging_service_sid=service_id,
            body=body,
            to=number,
        )
        # Update record that text has been sent / status of return
        write_json({"name": name, "body": message.body, "number": number,
                   "date": str(date.today()), "messageID": message.sid, "failed": False})
        print("\nSent message to {} with number: {}".format(name, number))
        return True
    except:
        write_json({"name": name, "body": body,
                   "number": number, "messageID": "null", "failed": True})
        print("\nCould not send message to: {} -> {}".format(
            name, number))
        return False


def sendAWSEmail(name: str, email: str, body: str, category: str, mailsender):
    # Create destination type
    destination = SesDestination(tos=[email])

    # Send mail and log response
    mailsender.send_email(
        destination=destination, subject="New Job Opportunity from Solution Based Therapeutics", text=body, source="gabe@solutionbasedtherapeutics.com", html="", name=name, category=category, email=email)


def checkSheetNameValidity(category: str, values: Data):
    """
        Check if there is a sheet name equal to the input  -> set isSheet to T/F
        Check if there is a drive folder equal to the input name -> set isFolder to T/F
        update the appropriate ID's for folderID and sheetID
    """

    try:
        # Get Sheet & Sheet ID
        service = build('sheets', 'v4', credentials=creds)
        request = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID, includeGridData=False)
        response = request.execute()

        sheetDict = dict()
        # Examine all of the pages we have in the Google Sheet (Recruitment-Prescreening)
        # Map each sheet name to the sheet ID
        for sheet in response.get('sheets'):
            s = sheet.get('properties')
            sheetDict[s.get('title')] = s.get('sheetId')

        # If our sheet is in the dicionary, set isSheet True, assign sheetId
        if category in sheetDict:
            values.isSheet = True
            values.sheetId = sheetDict.get(category, "")

        # Get Folder and Folder name
        """
        Ensure destination folder is exists and find it (Same name as Sheet Page)
        """
        service = build('drive', 'v3', credentials=creds)

        response = service.files().list(
            q="name='{}' and mimeType='application/vnd.google-apps.folder'".format(
                category),
            spaces='drive'
        ).execute()

        folderList = dict()
        for folder in response.get('files'):
            folderList[folder.get('name')] = folder.get('id')
        if category in folderList:
            values.isFolder = True
            values.folderId = folderList.get(category, "")

        return values
    except HttpError as err:
        print(err)
        return values


def setColumnVariables(inputdata: Data):
    """
    Assign position fields in inputdata before it is written to json
    """

    try:
        # Build Service
        service = build('sheets', 'v4', credentials=creds)

        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range="{}!1:1".format(inputdata.category)).execute()

        # Store results of sheet line 1

        for col in result['values'][0]:
            # Set the location of relevant columns for this sheet
            inputdata.positions.append(col)

        # Return Dictionary
        return inputdata
    except (HttpError, KeyError) as err:
        if (type(err) == KeyError):
            inputdata.err = "Error: the category you are trying to send a text in must include a: {} Column to interact with the program".format(
                err)
            return inputdata


def write_json(new_data, filename='records.json'):
    with open(filename, 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data
        file_data["records"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)


def curateLicenseList(licenselist: list[License], candidateData: candidateData):
    # For each match that we get
    for match in licenselist:
        # if fuzzywuzzy location similarity score is high enough, return proper info
        if fuzz.partial_ratio(candidateData.location.lower(), match.location.lower()) >= 75:
            # Assign License Name - Number
            candidateData.license_cert = "{} - {}".format(
                match.type, match.number)
            # Assign License Expiration
            candidateData.license_expiration = match.expiration
            return  # Break


def get_names(spreadsheet_id, sheet_name):
    try:
        service = build('sheets', 'v4', credentials=creds)
        our_range = sheet_name + "!A:A"

        # Call the Sheets API
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                     range=our_range).execute()
        # Get values array
        values = result.get('values', [])

        return values

    except HttpError as err:
        print(err)
    print("got all names")


def main():
    get_names(SPREADSHEET_ID, "Therapist")


if __name__ == '__main__':
    main()

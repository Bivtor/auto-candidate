from twilio.rest import Client
from dotenv import load_dotenv
from pydantic import BaseModel

import time
import os
import os.path
import json
import glob
from bs4 import BeautifulSoup

import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Amazon SES Send Email info
import logging

# import boto3
from botocore.exceptions import ClientError

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
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials2.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Gabe Sheet ID
SPREADSHEET_ID = '1c21ffEP_x-zzUKrxHhiprke724n9mEdY805Z2MphfXU'

class validData(BaseModel):
    isSheet: bool
    isFolder: bool
    sheetId: str
    folderId: str
    category: str
    nameCol: str | None = None
    phoneCol: str | None = None
    emailCol: str | None = None
    contactedCol: str | None = None
    timesContactedCol: str | None = None
    spokenToCol: str | None = None
    sourceCol: str | None = None
    locationCol: str | None = None
    dateAppliedCol: str | None = None
    err: str | None = None

class Data(BaseModel):
    password: str
    action: str
    category: str
    link: str = ""
    start: int = 2
    end: int = 1000
    message: str = ""
    messageType: str = ""
    calendy: str = ""

    # Sheet position info
    isSheet: bool = False
    isFolder: bool = False
    sheetId: str | None = None
    folderId: str | None = None
    nameCol: str | None = None
    phoneCol: str | None = None
    emailCol: str | None = None
    contactedCol: str | None = None
    timesContactedCol: str | None = None
    spokenToCol: str | None = None
    sourceCol: str | None = None
    locationCol: str | None = None
    dateAppliedCol: str | None = None
    err: str | None = None

def upload_basic(title, parents, path):
    """Insert new file.
    Returns : Id's of the file uploaded

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': title, 'parents': parents}
        media = MediaFileUpload(path, mimetype='application/pdf')

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File ID: {file.get("id")}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    print("Uploaded Resume with id: ", file.get('id'))
    return file.get('id')


def update_spreadsheet(info, SPREADSHEET_ID, SHEET_ID, folder_link):
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API to apply requests
        licenselist = info[6]
        licenselist2 = list()
        for i in licenselist:
            licenselist2.append(', '.join(i))

        data = {
            'requests': [
                {
                    "appendCells":
                    {
                        "sheetId": SHEET_ID,
                        "rows": [{
                            "values": [
                                {"userEnteredValue": {
                                    "formulaValue": "=HYPERLINK(\"{}\",\"{}\")".format(folder_link, info[0])}},
                                {"userEnteredValue": {
                                    "formulaValue": "=HYPERLINK(\"{}\",\"{}\")".format(info[7], info[1])}},
                                {"userEnteredValue": {"stringValue": info[2]}},
                                {"userEnteredValue": {"stringValue": info[3]}},
                                {"userEnteredValue": {"stringValue": info[4]}},
                                {"userEnteredValue": {"stringValue": info[5]}},
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

        #             [name_found, licensetype, licensenumber, licenseexpiration, licenselocation])
        # name = info[0]
        # reverse_name_format = name[name.rfind(" "):].strip(
        # ) + ", " + name[:name.rfind(" ")].strip()
        # print(licenselist)
        # print(licenselist2)
        # if (licenselist[0] != ''):
        #     name_in_reg = licenselist2[0][:[
        #         i for i, n in enumerate(licenselist2[0]) if n == ','][1]]
        #     isSame = SequenceMatcher(
        #         lambda x: x == " ", name_in_re2g.lower(), reverse_name_format.lower())
        #     licensenum = licensetype + " " + licenselist2[0][0]
        #     licenseexp = licenselist2[0][3]

        data2 = {
            'requests': [
                {
                    "appendCells":
                    {
                        "sheetId": SHEET_ID,
                        "rows": [{
                            "values": [
                                {"userEnteredValue": {
                                    "formulaValue": "=HYPERLINK(\"{}\",\"{}\")".format(folder_link, info[0])}},
                                {"userEnteredValue": {"stringValue": info[1]}},
                                {"userEnteredValue": {"stringValue": info[2]}},
                                {"userEnteredValue": {"stringValue": info[3]}},
                                {"userEnteredValue": {"stringValue": info[4]}},
                                {"userEnteredValue": {"stringValue": info[5]}},
                                # {"userEnteredValue": {
                                #     # "stringValue": licensenum}},
                                # {"userEnteredValue": {
                                #     "stringValue": licenseexp}}
                            ]}],
                        "fields": "userEnteredValue"
                    }
                }
            ]
        }

        # if (licenselist[0] != ''):
        #     print("Similarity Ratio of {}, {}: ".format(
        #         name_in_reg, reverse_name_format), isSame.ratio())
        #     if isSame.ratio() >= .9:
        #         data = data2

        request = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                                     body=data)
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

        # update said file with the items scraped from ziprecruiter
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

        # update said file with the items scraped from ziprecruiter
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


class candidateData(BaseModel):
    hasResume: bool
    location: str
    name: str
    phone: str
    email: str
    date: str
    ziprecruiter: str


def create_candidate(candidateData: candidateData, data):
    """
    Creates a new candidate inside xyz Folder and a new Questions document
    """

    # Set Proper Variables
    category = data['category']
    title = "{} {} ({})".format(candidateData.name,
                                category, candidateData.location)
    candidateData.date = cleanupdate(candidateData.date)
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
    # make sure license list is at least 5 long

    for i in range(5 - len(licenselist)):
        licenselist.append("")

    # update info for sheets insertion
    info2 = [candidateData.name, "Zip Recruiter", candidateData.location,
             candidateData.phone, candidateData.email, candidateData.date, licenselist, candidateData.ziprecruiter]

    folder_link = newParent[1]
    # call update spreadsheet function
    update_spreadsheet(info2, SPREADSHEET_ID, SHEET_ID, folder_link)

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


def cleanupdate(date):

    date2 = ""

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


def getLicenseInfo(name, depth) -> list:
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

    # fetch to CADC / RADT PAGE
    """
    fetch("https://ccapp.certemy.com/api/organization/public_registry/865beee9-c683-411c-a87e-cdf3d3fcd18e?&search=toby%20oskam&filters={%22last_name%22:[],%22certificationIds%22:[],%22organizationId%22:null}&page=1&page_size=20&order_id=last_name&order_type=asc", {
  "headers": {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "content-type": "application/json",
    "if-modified-since": "Thu, 03 Nov 2022 22:19:20 GMT",
    "sec-ch-ua": "\"Chromium\";v=\"106\", \"Google Chrome\";v=\"106\", \"Not;A=Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
  },
  "referrer": "https://ccapp.certemy.com/public-registry/865beee9-c683-411c-a87e-cdf3d3fcd18e",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "omit"
});

    """

    r = requests.post(url, data=body, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    count = 0
    licenseinfolist = list()
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
            [name_found, licensetype, licensenumber, licenseexpiration, licenselocation])

        count += 1

    print("Got {} licenses for {}".format(count, name))

    return licenseinfolist


def find_duplicates(creds, spreadsheet_id, sheet_name):
    try:
        service = build('sheets', 'v4', credentials=creds)

        range = sheet_name + "!A:A"
        # Call the Sheets API
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                     range=range).execute()
        values = result.get('values', [])
        duplicates = set()
        dupes = list()
        for i in values:
            i = str(i)
            if i in duplicates:
                dupes.append(i)
            else:
                duplicates.add(i)

        print(dupes)
        return dupes

    except HttpError as err:
        print(err)
    print("got all names")

# snippet-start:[python.example_code.ses.SesDestination]


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
# snippet-end:[python.example_code.ses.SesDestination]


class SesMailSender:
    """Encapsulates functions to send emails with Amazon SES."""

    def __init__(self, ses_client):
        """
        :param ses_client: A Boto3 Amazon SES client.
        """
        self.ses_client = ses_client

    def send_email(self, source, destination, subject, text, html, reply_tos=None):
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
                'Body': {'Text': {'Data': text}, 'Html': {'Data': html}}}}
        if reply_tos is not None:
            send_args['ReplyToAddresses'] = reply_tos
        try:
            response = self.ses_client.send_email(**send_args)
            message_id = response['MessageId']
            logger.info(
                "Sent mail %s from %s to %s.", message_id, source, destination.tos)
        except ClientError:
            logger.exception(
                "Couldn't send mail from %s to %s.", source, destination.tos)
            raise
        else:
            return message_id


def sendmailtexts(data: Data):
    # Find max length of the row insertion we will need
    max_length_row = max({data.nameCol, data.phoneCol, data.emailCol,
                         data.contactedCol, data.timesContactedCol, data.spokenToCol})+1

    try:
        sheetId = data.sheetId
        service = build('sheets', 'v4', credentials=creds)

        # TODO Create email identitity here

        for row in range(data.start, data.end):
            try:
                time.sleep(1)
                body = data.message
                RANGE = "{}!{}:{}".format(
                    data.category, row, row)
                result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                             range=RANGE).execute()
                values = result.get('values', [])[0]

                # If the length of the row is not as long as the furthest away category, extend it
                if len(values) < max_length_row:
                    for k in range(len(values), len(values) + max_length_row - len(values)):
                        values.append('')

                # Now we are able to access the proper items in rows before we batch update, because we know they all exist
                name = values[data.nameCol]
                number = values[data.phoneCol]
                email = values[data.emailCol]

                # Decide whether or not to send a text/email ###IMPORTANT
                def shouldSendMessage(data: Data, values: dict) -> bool:
                    if (values[data.spokenToCol] == 'N' or values[data.spokenToCol] == ''):
                        return True
                    else:
                        return False

                # Send message logic
                if shouldSendMessage(data, values):  # If we decide to send a message
                    values[data.spokenToCol] = 'N'
                    values[data.contactedCol] = 'T/'
                    if values[data.timesContactedCol] == '':

                        values[data.timesContactedCol] = '1'
                    else:
                        values[data.timesContactedCol] = str(
                            int(values[data.timesContactedCol])+1)

                    # Format body before sending final text
                    body = body.format(name, data.category, data.calendy)

                    # Send a text to the name / phone given
                    message_response = sendTwilioText(name, number, body)

                    # Update record that text has been sent / status of return
                    write_json(
                        {"name": name, "job": data.category, "number": number, "message_response_sid": message_response.sid, "message_response_err": message_response.error_code})
                    # TODO # Send an email to the name / email given
                    # TODO record that email has been sent / status of return

                    updatedata = {
                        'requests': [
                            {
                                "updateCells":
                                {
                                    "rows": [
                                        {
                                            "values": [
                                                {
                                                    "userEnteredValue": {"stringValue": values[data.contactedCol]}
                                                }
                                            ]
                                        }
                                    ],
                                    "fields": 'userEnteredValue',
                                    "start": {
                                        "sheetId": sheetId,
                                        "rowIndex": row-1,
                                        "columnIndex": data.contactedCol
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
                                                    "userEnteredValue": {"stringValue": values[data.timesContactedCol]}
                                                }
                                            ]
                                        }
                                    ],
                                    "fields": 'userEnteredValue',
                                    "start": {
                                        "sheetId": sheetId,
                                        "rowIndex": row-1,
                                        "columnIndex": data.timesContactedCol
                                    }
                                }
                            },
                        ]
                    }
                    request = service.spreadsheets().batchUpdate(
                        spreadsheetId=SPREADSHEET_ID,  body=updatedata).execute()

            except IndexError as err:
                print("Finished Texting and Emailing Candidaes")
                break

    except HttpError as err:
        print(err)


def sendTwilioText(name: str, number: str, body: str, ):
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
        print("Sent message to {} with number: {}".format(
            name, number))
        return message
    except:
        print("Could not send message to: {} @ {} (Their carrier most likely marked the message as spam)".format(
            name, number))
        return message


def sendAWSEmail():
    # Find AWS info for sending emails
    aws_user = os.getenv('aws_access_key_id')
    aws_pass = os.environ.get('aws_secret_access_key')
    pass



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
        for sheet in response.get('sheets'):
            s = sheet.get('properties')
            # print(sheet)
            sheetDict[s.get('title')] = s.get('sheetId')
        if category in sheetDict:  # if the Sheet is valid, update list
            values.isSheet = True
            values.sheetId = sheetDict.get(category, "")

        # Get Folder and Folder name
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
    try:
        # Build Service
        service = build('sheets', 'v4', credentials=creds)

        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range="{}!1:1".format(inputdata.category)).execute()

        # Store results of sheet line 1
        vals = dict()
        for i, col in enumerate(result['values'][0]):
            vals[col] = i

        # Set the location of relevant columns for this sheet
        inputdata.nameCol = vals['Name']
        inputdata.emailCol = vals['Email']
        inputdata.phoneCol = vals['Phone']
        inputdata.contactedCol = vals['Contacted']
        inputdata.timesContactedCol = vals['Times Contacted']
        inputdata.spokenToCol = vals['Spoken To']

        # Return Dictionary
        return inputdata
    except (HttpError, KeyError) as err:
        if (type(err) == KeyError):
            inputdata.err = "Error: the category you are trying to send a text in must include a: {} Column to interact with the program".format(
                err)
            return inputdata

# function to add to JSON


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


def main():
    pass


if __name__ == '__main__':
    main()

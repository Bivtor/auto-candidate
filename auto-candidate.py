from __future__ import print_function
import google.auth
from genericpath import isfile
from difflib import SequenceMatcher
from twilio.rest import Client
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from pathlib import Path

import time
import os
import os.path
import unicodedata
import urllib.parse
import urllib.request

import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Amazon SES Send Email info
import logging
import boto3
from botocore.exceptions import ClientError, WaiterError

logger = logging.getLogger(__name__)


load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/documents',
          'https://www.googleapis.com/auth/spreadsheets']


def upload_basic(creds, name, parents, path):
    """Insert new file.
    Returns : Id's of the file uploaded

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': name,
                         'parents': parents}
        media = MediaFileUpload(path,
                                mimetype='application/pdf')

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File ID: {file.get("id")}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    print("Uploaded Resume with id: ", file.get('id'))
    return file.get('id')


def update_spreadsheet(creds, info, parents, SPREADSHEET_ID, SHEET_ID, folder_link, licensetype):
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
                                {"userEnteredValue": {"stringValue": info[1]}},
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


def create_file_LVN(creds, info: list, parents, name):
    # create file
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'mimeType': 'application/vnd.google-apps.document',
            'name': name,
            'parents': parents
        }
        file = service.files().create(body=file_metadata, fields='id',
                                      ).execute()
        print(F'Document was created with ID: "{file.get("id")}".')

        ###########################################
        inputName = "Name: " + info[5] + "\n"
        inputPhone = "Phone: " + info[1] + "\n"
        inputEmail = "Email: " + info[2] + "\n"
        inputDate = "Date Applied: " + info[3] + "\n"
        inputLocation = "Location: " + info[4] + "\n"
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
                        'text': "LVN INTERVIEW QUESTIONS\n"
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': 25,
                        },
                        'text': inputName,
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputName)+25,
                        },
                        'text': inputPhone
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+25,
                        },
                        'text': inputEmail
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+25 + len(inputEmail)
                        },
                        'text': inputDate
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+25 + len(inputEmail) + len(inputDate)
                        },
                        'text': inputLocation
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+25 + len(inputEmail) + len(inputDate) + len(inputLocation)
                        },
                        'text': bigString
                    }
                },
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex':  25
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
                            'endIndex':  len(inputPhone) + len(inputName)+25 + len(inputEmail) + len(inputDate) + len(inputLocation) + len(bigString)
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


def create_file_Therapist(creds, info: list, parents, name):
    # create file
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'mimeType': 'application/vnd.google-apps.document',
            'name': name,
            'parents': parents
        }
        file = service.files().create(body=file_metadata, fields='id',
                                      ).execute()
        print(F'Document was created with ID: "{file.get("id")}".')

        ###########################################
        inputName = "Name: " + info[5] + "\n"
        inputPhone = "Phone: " + info[1] + "\n"
        inputEmail = "Email: " + info[2] + "\n"
        inputDate = "Date Applied: " + info[3] + "\n"
        inputLocation = "Location: " + info[4] + "\n"
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
                            'endIndex':  25
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
                            'endIndex':  len(inputPhone) + len(inputName)+25 + len(inputEmail) + len(inputDate) + len(inputLocation) + len(bigString)
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


def create_folder(creds, name: str, parents):
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


def add_candidates(creds):

    ##################################################################
    # assign directory
    directory = '/Users/victorrinaldi/Desktop/auto_candidate/candidates'
    # iterate over files in that directory

    ########################################################
    # Driver code, uploads pdf and documents of every folder associated inside candidates
    ########################################################

    for folder in sorted(os.listdir(directory)):
        if (folder == '.DS_Store'):
            continue
        items = sorted(os.listdir(os.path.join(directory, folder)))
        if len(items) == 0:
            continue
        pdf = None

        page_html = os.path.join(os.path.join(directory, folder), items[0])

        if len(items) == 3:  # no resume
            pdf = os.path.join(os.path.join(directory, folder), items[2])
        else:
            pdf = None

        print(folder)

        # therapists or LVN

        # path = create_Therapist(creds, page_html)
        path = create_LVN(creds, page_html)
        if pdf:
            # print("would upload")
            upload_basic(creds, path[0], path[1], pdf)


def create_LVN(creds, path) -> list:
    """
    Creates a new LVN candidate inside the LVN Folder and a new LVN document
    """

    # get info from html
    info = getLVNInfo(path)
    title = info[0]
    phone = info[1]
    email = info[2]
    date = info[3]
    location = info[4]
    name = info[5]

    # return [name, phone, email, date, location, nameonly]

    # assign parent for LVN folder
    # GABE
    parents = ['18iotkvD56CLbdrVKJGPewjC1MIeu__hk']
    SPREADSHEET_ID = '1c21ffEP_x-zzUKrxHhiprke724n9mEdY805Z2MphfXU'
    SHEET_ID = 1087287054  # NURSES
    # SHEET_ID = 1274126071  # CASE MANAGER

    # KK10
    # parents = ['1ufXmmOK1w_YRUzqzmiZPPXOWQDoemNX2']
    # SPREADSHEET_ID = '1PPTbe9q0g9xjSwm2Jox2FTsJKQN6Q3WfcYPAHx5DXhA'
    # SHEET_ID = 0

    # add id of new parent so that we are inside the proper file
    newParent = create_folder(creds, title, parents)
    folder_id = [newParent[0]]
    folder_link = newParent[1]
    # crate Questions Document
    create_file_LVN(creds, info, folder_id, title)

   # Get License number of first (depth) entries:
    licenselist = getLicenseInfo(name, 5)
    # make sure license list is at least 5 long
    for i in range(5 - len(licenselist)):
        licenselist.append("")

    # update info for sheets insertion
    info2 = [name, "Zip Recruiter", location, phone, email, date, licenselist]

    folder_link = newParent[1]
    # call update spreadsheet function
    update_spreadsheet(creds, info2, parents,
                       SPREADSHEET_ID, SHEET_ID, folder_link, "LVN")

    return [title, folder_id]


def create_Therapist(creds, path):
    """
    Creates a new Therapist candidate inside the Therapist Folder and a new Therapist document
    """

    # get info from html
    info = getTherapistInfo(path)
    title = info[0]
    phone = info[1]
    email = info[2]
    date = info[3]
    location = info[4]
    name = info[5]

    # return [name, phone, email, date, location, nameonly]

    # assign parent for Therapist folder

    # GABE
    parents = ['15WDRlTToaRXbYRc-6tDlhlEa2x1Flwx2']
    SPREADSHEET_ID = '1c21ffEP_x-zzUKrxHhiprke724n9mEdY805Z2MphfXU'
    SHEET_ID = 444685763

    # KK10
    # parents = ['1jtuVaA62GOLnQLXBarid4AtvbKRmhGij']
    # SPREADSHEET_ID = '1PPTbe9q0g9xjSwm2Jox2FTsJKQN6Q3WfcYPAHx5DXhA'
    # SHEET_ID = 1406139361

    # add id of new parent so that we are inside the proper file
    print("Creating", info[5], "Folder")
    newParent = create_folder(creds, title, parents)
    folder_id = [newParent[0]]
    folder_link = newParent[1]
    # crate Questions Document
    create_file_Therapist(creds, info, folder_id, title)

    # Get License number of first (depth) entries:
    licenselist = getLicenseInfo(name, 5)
    # make sure license list is at least 5 long
    for i in range(5 - len(licenselist)):
        licenselist.append("")
    # update info for sheets insertion
    info2 = [name, "Zip Recruiter", location, phone, email, date, licenselist]

    folder_link = newParent[1]
    # call update spreadsheet function
    update_spreadsheet(creds, info2, parents,
                       SPREADSHEET_ID, SHEET_ID, folder_link, "Therapist")

    return [title, folder_id]


def getLVNInfo(path) -> list:
    """
    Find Name and Location from HTML (LVN Specific)
    """
    with open(path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    name = ""
    location = ""

    # find name
    name = soup.find('h4', class_='name').string.strip()
    name += " LVN "

    scr = ""
    phone = ""
    email = ""
    date = ""

    scr = soup.find(class_="side_content ats_content").find(
        'p', class_="location")

    # fixing no location exception
    if scr == None:
        scr = soup.find('a', class_='manage_job_link').stripped_strings
        for s in scr:
            scr = s
        scr = scr[scr.find(" - ")+3:]
    else:
        scr = scr.string

    scr = str(scr)
    scr = scr[:scr.find(',')]
    scr = '(' + scr + ')'
    name += scr
    name = name.strip()
    location = scr[1:len(scr)-1].strip()

    ###############
    for text in soup.find_all(class_="textPhone"):
        phone = text
    phone = phone.string

    for mail in soup.find_all(class_="textEmail"):
        email = mail
    email = mail.string

    date = soup.find(class_="text applied_date").span.string

    date = cleanupdate(date)

    # update name to remove LVN (Location)
    nameonly = name[:name.find("LVN")]

    # inputName = "Name: " + info[0] + "\n"
    # inputPhone = "Phone: " + info[1] + "\n"
    # inputEmail = "Email: " + info[2] + "\n"
    # inputDate = "Date Applied: " + info[3] + "\n"
    # inputLocation = "Location: " + info[4] + "\n"
    return [name, phone, email, date, location, nameonly.strip()]


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


def getTherapistInfo(path) -> list:
    """
    Find Name and Location from HTML (Therapist Specific)
    """
    with open(path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    name = ""
    location = ""

    # find name
    name = soup.find('h4', class_='name').string.strip()
    name += " Therapist "

    scr = ""
    phone = ""
    email = ""
    date = ""

    scr = soup.find(class_="side_content ats_content").find(
        'p', class_="location")

    # fixing no location exception
    if scr == None:
        scr = soup.find('a', class_='manage_job_link').stripped_strings
        for s in scr:
            scr = s
        scr = scr[scr.find(" - ")+3:]
    else:
        scr = scr.string

    # if (scr.string == None): scr = soup.find
    scr = str(scr)
    scr = scr[:scr.find(',')]
    scr = '(' + scr + ')'
    name += scr
    name = name.strip()
    location = scr[1:len(scr)-1].strip()

    ###############
    for text in soup.find_all(class_="textPhone"):
        phone = text
    phone = phone.string

    for mail in soup.find_all(class_="textEmail"):
        email = mail
    email = mail.string

    date = soup.find(class_="text applied_date").span.string
    date = cleanupdate(date)

    # update name to remove LVN (Location)
    nameonly = name[:name.find("Therapist")]

    # inputName = "Name: " + info[0] + "\n"
    # inputPhone = "Phone: " + info[1] + "\n"
    # inputEmail = "Email: " + info[2] + "\n"
    # inputDate = "Date Applied: " + info[3] + "\n"
    # inputLocation = "Location: " + info[4] + "\n"
    return [name, phone, email, date, location, nameonly.strip()]


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


def sendTwilioTexts(creds, spreadsheet_id, sheet_name, sheet_id):
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Find your Account SID and Auth Token and Message
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        service_id = os.environ['TWILIO_SERVICE_ID']
        aws_user = os.getenv('aws_access_key_id')
        aws_pass = os.environ.get('aws_secret_access_key')

        client = Client(account_sid, auth_token)
        calendar_link = 'calendly.com/gabe_berko'

        # Get the Sheets Info on whether or not to Text/Email
        for i in range(2, 992):
            time.sleep(1)
            r = sheet_name + "!A{}:J{}".format(i, i)
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=r).execute()
            try:
                values = result.get('values', [])[0]
            except IndexError as err:
                print("No more candidates: ({})".format(err))
                break

            # Choose whether or not to Send Text/Message
            if len(values) < 10:  # if there is no Contacted category inputted
                contacted = "N"
            else:
                contacted = values[9]
            name = values[0]
            number = values[3]

            # TODO Make sure errors are caught from wrong phone number

            # Send Text if 'N' marked in the column J
            if len(contacted) == 0 or contacted[0].lower() == 'n':
                body = ""
                if sheet_name == "Therapists":
                    body = "Hello {}!\n\nThis is Gabe from SBT. We received your resume via Zip Recruiter for the Therapist role!\n\nI'd love to schedule a phone interview with you here: {}\n\nIf you have any questions, you can call/text my personal cell at (310) 920-9349".format(
                        name, calendar_link)
                elif sheet_name == "Nurses":
                    body = "Hello {}!\n\nThis is Gabe from SBT. We received your resume via Zip Recruiter for the Nursing role!\n\nI'd love to schedule a phone interview with you here: {}\n\nIf you have any questions, you can call/text my personal cell at (310) 920-9349".format(
                        name, calendar_link)
                elif sheet_name == "RADT":
                    body = "Hello {}!\n\nThis is Gabe from SBT. We received your resume via Zip Recruiter for the Tech role!\n\nI'd love to schedule a phone interview with you here: {}\n\nIf you have any questions, you can call/text my personal cell at (310) 920-9349".format(
                        name, calendar_link)
                else:
                    body = "Hello {}!\n\nThis is Gabe from SBT. We received your resume via Zip Recruiter!\n\nI'd love to schedule a phone interview with you here: {}\n\nIf you have any questions, you can call/text my personal cell at (310) 920-9349".format(
                        name, calendar_link)
                try:
                    message = client.messages.create(
                        messaging_service_sid=service_id,
                        body=body,
                        to=number,
                    )
                    print("Sent message to {} with message SID: {}".format(
                        name, message.sid))
                    contacted = 'Y'
                    textemail = 'T/'
                except:
                    print("Message was not sent to: {} - {}".format(
                        name, number))
                    print("This text did not send at row i=", i)
                    contacted = 'N'  # Contacted stays N
                    textemail = 'N/'

                ###########################    ########################### ###########################

                # Update spreadsheet to reflect text has been sent 'Y/#'
                data = {
                    'requests': [
                        {
                            "updateCells":
                            {
                                "rows": [
                                    {
                                        "values": [
                                            {"userEnteredValue": {
                                                "stringValue": textemail}},
                                            {"userEnteredValue": {
                                                "stringValue": contacted}},

                                        ]}],
                                "fields": 'userEnteredValue',
                                "start": {
                                    "sheetId": sheet_id,
                                    "rowIndex": i-1,
                                    "columnIndex": 8
                                }
                            }
                        }
                    ]
                }
                request = service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,  body=data)
                response = request.execute()
    except HttpError as err:
        print(err)


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
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

    ##################################################################
    ##################################################################
    ################## s################################################
    # GABE
    # parents = ['15WDRlTToaRXbYRc-6tDlhlEa2x1Flwx2']
    SPREADSHEET_ID = '1c21ffEP_x-zzUKrxHhiprke724n9mEdY805Z2MphfXU'
    # SHEET_ID = 444685763 #Therapists
    SHEET_ID = 1087287054  # Nurses
    # KK10
    # parents = ['1jtuVaA62GOLnQLXBarid4AtvbKRmhGij']
    # SPREADSHEET_ID = '1PPTbe9q0g9xjSwm2Jox2FTsJKQN6Q3WfcYPAHx5DXhA'
    # SHEET_ID = 1406139361

    # add_candidates(creds)
    # sendTwilioTexts(creds, SPREADSHEET_ID, "Nurses", SHEET_ID)
    print("ran main")


if __name__ == '__main__':
    main()

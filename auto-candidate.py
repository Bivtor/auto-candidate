from __future__ import print_function
from genericpath import isfile

import os
import os.path
import urllib.parse
import urllib.request
from pathlib import Path


from venv import create
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from bs4 import BeautifulSoup

import google.auth


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/documents',
          'https://www.googleapis.com/auth/spreadsheets']

# TODO make this work, post request body data doesnt seem to do anything


def getLVNnumber():
    url = 'https://search.dca.ca.gov/results'
    values = {"referrer": "https://search.dca.ca.gov/",
              "referrerPolicy": "strict-origin-when-cross-origin",
              "body": "boardCode=0&licenseType=248&licenseNumber=&busName=&firstName=rose&lastName=arenas&registryNumber=",
              "method": "POST",
              "mode": "cors",
              "credentials": "include"}
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua": "\"Chromium\";v=\"106\", \"Google Chrome\";v=\"106\", \"Not;A=Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }
    filename = Path('index.html')

    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')  # data should be bytes
    req = urllib.request.Request(url, data)
    file2 = open("MyFile2.txt", "wb")
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        # filename = encodebytes(response)
        # print(the_page)
        file2.write(the_page)
        file2.close()
        print("Downloaded LVN HTML for: " + "TODO")


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

    return file.get('id')


def update_spreadsheet(creds, info, parents, SPREADSHEET_ID, SHEET_ID, folder_link):
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API to apply requests

        # Change name to remove extra text
        info[0] = info[0][:info[0].find("LVN")]

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
                                {"userEnteredValue": {"stringValue": info[6]}}
                            ]}],
                        "fields": "userEnteredValue"
                    }
                }
            ]
        }

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
        print(F'File was created with ID: "{file.get("id")}".')

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

            print('Updated document with ID: {0}'.format(
                doc.get('id')))

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
        print(F'File was created with ID: "{file.get("id")}".')

        ###########################################
        inputName = "Name: " + info[5] + "\n"
        inputPhone = "Phone: " + info[1] + "\n"
        inputEmail = "Email: " + info[2] + "\n"
        inputDate = "Date Applied: " + info[3] + "\n"
        inputLocation = "Location: " + info[4] + "\n"
        certification = "Certification Type and #:\n"
        verification = "Verified/Expiration?:\n"
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
                        'text': certification
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+31 + len(inputEmail) + len(inputDate) + len(inputLocation) + len(certification)
                        },
                        'text': verification
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': len(inputPhone) + len(inputName)+31 + len(inputEmail) + len(inputDate) + len(inputLocation) + len(certification) + len(verification)
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
                            'endIndex':  len(inputPhone) + len(inputName)+25 + len(inputEmail) + len(inputDate) + len(inputLocation) + len(certification) + len(verification) + len(bigString)
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

            print('Updated document with ID: {0}'.format(
                doc.get('id')))

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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    ##################################################################
    # assign directory
    directory = '/Users/victorrinaldi/Desktop/auto_candidate/candidates'
    # iterate over files in that directory

    ########################################################
    # Driver code, uploads pdf and documents of every folder associated inside candidates
    ########################################################
    for folder in os.listdir(directory):
        items = os.listdir(os.path.join(directory, folder))
        pdf = None
        page_html = None
        if (items[0].find('pdf') > 0):
            pdf = items[0]
            page_html = items[1]
        else:
            pdf = items[1]
            page_html = items[0]
        pdf = os.path.join(os.path.join(directory, folder), pdf)
        page_html = os.path.join(os.path.join(directory, folder), page_html)

        # choose create LVN or create Therapist
        if (page_html.find("Therapist") > 0):
            path = create_Therapist(creds, page_html)
            upload_basic(creds, path[0], path[1], pdf)
        else:
            path = create_LVN(creds, page_html)
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
    # parents = ['18iotkvD56CLbdrVKJGPewjC1MIeu__hk']
    # KK10
    parents = ['1ufXmmOK1w_YRUzqzmiZPPXOWQDoemNX2']

    # add id of new parent so that we are inside the proper file
    newParent = create_folder(creds, title, parents)
    folder_id = [newParent[0]]
    folder_link = newParent[1]
    # crate Questions Document
    create_file_LVN(creds, info, folder_id, title)

    # SPREADSHEET ID
    # GABE
    # SPREADSHEET_ID = '1c21ffEP_x-zzUKrxHhiprke724n9mEdY805Z2MphfXU'
    # KK10
    SPREADSHEET_ID = '1PPTbe9q0g9xjSwm2Jox2FTsJKQN6Q3WfcYPAHx5DXhA'
    # SHEET ID for LVN
    # GABE
    # SHEET_ID = 1087287054
    # KK10
    SHEET_ID = 0

    # TODO add LVN number from website
    # update info for sheets insertion
    info2 = [name, "Zip Recruiter", location, phone, email, date, "LVN - "]

    folder_link = newParent[1]
    # call update spreadsheet function
    update_spreadsheet(creds, info2, parents,
                       SPREADSHEET_ID, SHEET_ID, folder_link)

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
    # parents = ['15WDRlTToaRXbYRc-6tDlhlEa2x1Flwx2']
    # KK10
    parents = ['1jtuVaA62GOLnQLXBarid4AtvbKRmhGij']

    # add id of new parent so that we are inside the proper file
    newParent = create_folder(creds, title, parents)
    folder_id = [newParent[0]]
    folder_link = newParent[1]
    # crate Questions Document
    create_file_Therapist(creds, info, folder_id, title)

    # SPREADSHEET ID
    # GABE
    # SPREADSHEET_ID = '1c21ffEP_x-zzUKrxHhiprke724n9mEdY805Z2MphfXU'
    # KK10
    SPREADSHEET_ID = '1PPTbe9q0g9xjSwm2Jox2FTsJKQN6Q3WfcYPAHx5DXhA'
    # SHEET ID for Therapist
    # GABE
    # SHEET_ID = 444685763
    # KK10
    SHEET_ID = 1406139361

    # TODO add LVN number from website
    # update info for sheets insertion
    info2 = [name, "Zip Recruiter", location, phone, email, date, ""]

    folder_link = newParent[1]
    # call update spreadsheet function
    update_spreadsheet(creds, info2, parents,
                       SPREADSHEET_ID, SHEET_ID, folder_link)

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
    for div in soup.h1:
        name = div
    name = name.strip()
    name += " LVN "

    scr = ""
    phone = ""
    email = ""
    date = ""

    scr = soup.find(class_="side_content ats_content").p.string
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
        date2 += findMonth("Jun")
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

    # update name to remove LVN (Location)
    nameonly = name[:name.find("LVN")]

    # inputName = "Name: " + info[0] + "\n"
    # inputPhone = "Phone: " + info[1] + "\n"
    # inputEmail = "Email: " + info[2] + "\n"
    # inputDate = "Date Applied: " + info[3] + "\n"
    # inputLocation = "Location: " + info[4] + "\n"
    return [name, phone, email, date, location, nameonly]


def getTherapistInfo(path) -> list:
    """
    Find Name and Location from HTML (Therapist Specific)
    """
    with open(path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    name = ""
    location = ""

    # find name
    for div in soup.h1:
        name = div
    name = name.strip()
    name += " Therapist "

    scr = ""
    phone = ""
    email = ""
    date = ""

    scr = soup.find(class_="side_content ats_content").p.string
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
        date2 += findMonth("Jun")
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

    # update name to remove LVN (Location)
    nameonly = name[:name.find("Therapist")]

    # inputName = "Name: " + info[0] + "\n"
    # inputPhone = "Phone: " + info[1] + "\n"
    # inputEmail = "Email: " + info[2] + "\n"
    # inputDate = "Date Applied: " + info[3] + "\n"
    # inputLocation = "Location: " + info[4] + "\n"
    return [name, phone, email, date, location, nameonly]


if __name__ == '__main__':
    main()

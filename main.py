from auto_candidate import *

from pydantic import BaseModel
import os
import json
import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from hashlib import sha256

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class textData(BaseModel):
    category_texts: str


def openstring(data: Data):
    print("Opening Link: {}".format(data.link))
    cmd = 'start chrome {}'.format(data.link)  # OPEN chrome
    if os.system(cmd) != 0:
        return False


@app.post('/runfunction')
def createUsers(candidateData: candidateData):
    f = open('settings.json')
    data = json.load(f)
    create_candidate(candidateData, data)
    f.close()
    print(candidateData.name)
    return {"Success"}


class ResponseModel(BaseModel):
    response: str


@app.post('/submitdata')
def submitdata(data: Data):
    # Check if operation is currently in progress
    f = open('isWorking.json')
    json_check = json.load(f)
    f.close()

    # If there is a current process, return checkModel with its"not_working_response"
    if json_check['isWorking']:
        return ResponseModel(response="Operation Ongoing")

    # Set that there is now an operation ongoing since we passed the check
    json_check['isWorking'] = True
    with open("isWorking.json", "w") as outfile:
        json.dump(json_check, outfile)

    # Check Password
    if data.password != os.environ['DEFAULT_PASSWORD']:
        return "Incorrect Password"

    # Check Validity
    checkSheetNameValidity(data.category, data)
    if ((not data.isFolder) and (not data.isSheet)):
        return "Folder or Sheet name does not exactly match category"

    # Set Variables
    setColumnVariables(data)

    # Write data to a file for use if adding candidates
    with open("settings.json", "w") as outfile:
        outfile.write(data.json())
    print("Successfully Set Column Variables")

    ################## Passed Pre-Checks ##################
    if data.action == "Text":
        sendmailtexts(data)
    if data.action == "Add":
        openstring(data)

    # Stop Working
    json_check['isWorking'] = False
    with open("isWorking.json", "w") as outfile:
        json.dump(json_check, outfile)

    return ResponseModel(response="Success")


class MailData(BaseModel):
    message: dict


@app.post('/retrieve_email')
def createUsers(data: MailData):
    # Decode message
    response = base64.b64decode(data.message['data'])

    # Convert bytes to string using `decode()` method
    response_str = response.decode('utf-8')

    # Convert JSON string to Python object using `json.loads()` function
    response_json = json.loads(response_str)

    # Get message
    process_message(user_id=response_json['emailAddress'],
                    history_id=response_json['historyId'])

    return 200


def submitdata_clone(data: Data):
    # Check if operation is currently in progress
    f = open('isWorking.json')
    json_check = json.load(f)
    f.close()

    # If there is a current process, return checkModel with its"not_working_response"
    if json_check['isWorking']:
        # TODO Indicate that we were working and could not add a candidate
        print("Could not add candidate")
        return 200

    # Set that there is now an operation ongoing since we passed the check
    json_check['isWorking'] = True
    with open("isWorking.json", "w") as outfile:
        json.dump(json_check, outfile)

    # Check Password
    if data.password != os.environ['DEFAULT_PASSWORD']:
        return "Incorrect Password"

    # Check Validity
    checkSheetNameValidity(data.category, data)
    if ((not data.isFolder) and (not data.isSheet)):
        return "Folder or Sheet name does not exactly match category"

    # Set Variables
    setColumnVariables(data)

    # Write data to a file for use if adding candidates
    with open("settings.json", "w") as outfile:
        outfile.write(data.json())
    print("Successfully Set Column Variables")

    ################## Passed Pre-Checks ##################
    if data.action == "Text":
        sendmailtexts(data)
    if data.action == "Add":
        openstring(data)

    # Stop Working
    json_check['isWorking'] = False
    with open("isWorking.json", "w") as outfile:
        json.dump(json_check, outfile)

    # Always return a value
    return 200


def process_message(user_id, history_id):
    try:
        service = build('gmail', 'v1', credentials=creds)

        # Get list of last (1) message ID's
        messages = service.users().messages().list(
            userId='me', maxResults=1).execute()

        # Get ID of last message
        message = messages['messages'][0]['id']

        # Get raw_data of last message (Becasue the raw data contains the url we want and not the non raw for some reason)
        message = service.users().messages().get(
            userId='me', id=message, format='raw').execute()

        # Decode raw_data
        raw_message = base64.urlsafe_b64decode(
            message['raw'].encode('utf-8')).decode('utf-8')

        # Check if the text contains a URL in the format "https://www.ziprecruiter.com/contact/response/*/*"
        pattern = r'https://www\.ziprecruiter\.com/contact/response/[^/]*/[^/]*\?'
        match = re.search(pattern, raw_message)

        # Check if email contains text we want
        if match:
            candidate_url = match.group(0)
            print(f'Found URL: {candidate_url}')

            # Get candidate name
            loc = raw_message.find("New Candidate:")
            candidate_name = raw_message[loc+15:loc+100]
            candidate_name = candidate_name[:candidate_name.find(
                "for")].strip()
            print("Candidate name", candidate_name)

            # Get job title
            loc = raw_message.find("for '")
            job_title = raw_message[loc+5: loc+100]
            job_title = job_title[:job_title.find("'")].lower().strip()
            print("Job title", job_title)

            # Load the pre-determined associations of job titles -> spreadsheet name
            with open('name_map.json') as f:
                name_map: dict = json.load(f)

                # If the job_title exists in our map of titles
      #              if job_title in name_map:

                    # Deterine which category the candidate should be added to
                sheet_destination = "Therapist"# name_map[job_title] "Therapist"

                # Get entire column 1 (names column)
                names_list = get_names(
                    spreadsheet_id=SPREADSHEET_ID, sheet_name=sheet_destination)

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
                submitdata_clone(data=can_data)

                # TODO Get the last line of the spreadsheet
                # TODO Call the send text function for only the last line of the spreadsheet
            # else:
            #     print("Could not find job type -> google sheet association")

        # else:
        #     print('No matching URL found in the body.')

    except HttpError as error:
        print(f'An error occurred: {error}')


@app.post('/sendtexts')
def sendtexts():
    f = open('settings.json')
    data = json.load(f)
    sendmailtexts(data)
    f.close()
    return {"Success"}

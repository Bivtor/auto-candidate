from auto_candidate import *
from email_handler import process_message, updateCandidateExistence

from pydantic import BaseModel
import os
import json
import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from hashlib import sha256
from auto_candidate import logger

app = FastAPI()


# Log Server start
logger.info('Started Server')

# Load environmental variables
load_dotenv()


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
    # Add candidate with saved data
    create_candidate(candidateData, data)
    f.close()
    
    # Log
    logger.info(f'Created profile for {candidateData.name}')

    # Update Candidate Existence
    updateCandidateExistence(
        SPREADSHEET_ID, sheet_name=data['category'])
    
    # Log
    logger.info(f'Updated local json file for {candidateData.name}')

    return {"message": "Success"}


class ResponseModel(BaseModel):
    response: str


@app.post('/submitdata')
def submitdata(data: Data):
    # Check if operation is currently in progress
    f = open('isWorking.json')
    json_check = json.load(f)
    f.close()

    # Check Password
    if data.password != os.environ['DEFAULT_PASSWORD']:
        return ResponseModel(response="Incorrect Password")

    # If there is a current process, return checkModel with its"not_working_response"
    if json_check['isWorking']:
        return ResponseModel(response="Operation Ongoing")

    # Set that there is now an operation ongoing since we passed the check
    json_check['isWorking'] = True
    with open("isWorking.json", "w") as outfile:
        json.dump(json_check, outfile)

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
    logger.info('Recieved New Email notification')

    # Get message
    process_message()

    return 200






def prevent_duplicates(inputname: str):

    # Check if the file exists
    if os.path.isfile(NAMESFILEPATH):
        # File exists, load the JSON data
        with open(NAMESFILEPATH, "r") as json_file:
            data = json.load(json_file)
            # Check if the 'names' key exists and contains a string
            if inputname in data['names']:
                return True
            else:
                return False
    else:
        # File does not exist, create the JSON file and add the names from the database
        # TODO: Add code to populate the 'names' list

        # Save the JSON data to the file
        with open(NAMESFILEPATH, "w") as json_file:
            json.dump(data, json_file)





@app.post('/sendtexts')
def sendtexts():
    f = open('settings.json')
    data = json.load(f)
    sendmailtexts(data)
    f.close()
    return {"Success"}

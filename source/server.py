from partial_add_seq import *
from auto_candidate import *
from paths import *
from email_handler import process_message, updateCandidateExistence, decideTokenRefresh

from pydantic import BaseModel
import os
import sys
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
load_dotenv(dotenv_path=ENV_PATH)


origins = [
    "http://localhost",
    "http://localhost:3001",
    "http://localhost:3000",
    "https://www.vrinaldi.com",
    "https://vrinaldi.com",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8000/submitdata",
    "https://127.0.0.1:8000"
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


# def receive_signal(signalNumber, frame):
#     print('Received:', signalNumber)
#     sys.exit()


# @app.on_event("startup")
# async def startup_event():
#     import signal
#     print("startup")
#     signal.signal(signal.SIGINT, receive_signal)
#     # startup tasks


def openstring(data: Data):
    cmd = 'open -a "Google Chrome"  \"{}\"'.format(data.link)  # OPEN chrome
    if os.system(cmd) == 0:
        logger.info(f"Successfully Opened Link: {data.link}")
    else:
        logger.info(f"Failed to open link: {data.link}")


@app.post('/runfunction')
def createUsers(candidateData: candidateData):
    f = open(SETTINGS_PATH)
    data = json.load(f)

    # Add candidate with saved data
    create_candidate(candidateData, data)

    # Testing
    # print(f"recieved new request with: \n {candidateData}")
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
    if checkWorking():
        logger.info("Operation currently ongoing, cannot process, stopping")
        return ResponseModel(response="Currently Busy")

    # Check Password
    if data.password != os.environ['DEFAULT_PASSWORD']:
        return ResponseModel(response="Incorrect Password")

    # Set that there is now an operation ongoing since we passed the check
    setWorking(True)

    # Check Validity
    checkSheetNameValidity(data.category, data)
    if ((not data.isFolder) and (not data.isSheet)):
        logger.info("Folder or Sheet name does not exactly match category")
        setWorking(False)
        return "Folder or Sheet name does not exactly match category"

    # Set Variables
    setColumnVariables(data)

    # Write data to a file for use if adding candidates
    with open(SETTINGS_PATH, "w") as outfile:
        outfile.write(data.json())
    logger.info("Successfully Set Column Variables")

    ################## Passed Pre-Checks ##################
    if data.action == "Text":
        sendmailtexts(data)
    if data.action == "Add":
        openstring(data)

    # Stop Working
    setWorking(False)

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

    # Refresh the publish token
    decideTokenRefresh(WORKING_PATH)

    # Get message
    process_message()

    return 200


def prevent_duplicates(inputname: str):

    # Check if the file exists
    if os.path.isfile(NAMES_PATH):
        # File exists, load the JSON data
        with open(NAMES_PATH, "r") as json_file:
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
        with open(NAMES_PATH, "w") as json_file:
            json.dump(data, json_file)


@app.post('/sendtexts')
def sendtexts():
    f = open(SETTINGS_PATH)
    data = json.load(f)
    sendmailtexts(data)
    f.close()
    return {"Success"}


@app.post('/submit_candidate')
async def submit_candidate(candidateData: candidateData):

    # Gather destination info
    f = open(SETTINGS_PATH)
    data = json.load(f)

    # Perform first half candidate add
    await beginHalfAdd(candidateData, data)
    f.close()

    # Log
    logger.info(f'Completed 1/2 profile for {candidateData.name}')

    # Update Candidate Existence
    updateCandidateExistence(
        SPREADSHEET_ID, sheet_name=data['category'])

    # Log
    logger.info(f'Updated local json file for {candidateData.name}')

    # Check whether or not we are already working on finishing resume downloads, always try to call.
    while (1):
        if not await checkIsUpdating():
            await setIsUpdating(True)
            # await finishHalfAdd(candidateData, data, title)
            finished = False
            while (not finished):
                finished = await finishHalfAdd(candidateData, data, "TEMPORARY TITLE")
                print(f"finished is: {finished}")
            await setIsUpdating(False)
            break
        time.sleep(1)

    return {"message": "Success"}

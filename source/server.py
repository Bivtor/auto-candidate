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
from celery import Celery
from worker import *

app = FastAPI()

# celeryapp = Celery(
#     'server', broker='amqp://guest:guest@127.0.0.1:5672'
# )

# sudo rabbitmq-server
# sudo rabbitmqctl status
# sudo rabbitmqctl stop


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
    """
    Submit a Task to the Broker with the current settings stored 
    """

    # Load stored settings data
    f = open(SETTINGS_PATH)
    setting_data = json.load(f)

    # Concatonate dictionaries to send all of the data to
    candidate_dict = candidateData.dict()
    candidate_dict.update(setting_data)

    # Submit Task Part 1
    process_candidate_part1.delay(candidate_dict)

    # TODO Submit Task Part 2

    # Log
    # logger.info(f'Created profile for {candidateData.name}')

    # Update Candidate Existence
    # updateCandidateExistence(
    #     SPREADSHEET_ID, sheet_name=data['category'])

    # Log
    # logger.info(f'Updated local json file for {candidateData.name}')

    f.close()
    return {"message": "Successfully opened link on Test Branch build"}


class ResponseModel(BaseModel):
    response: str


@app.post('/submitdata')
def submitdata(data: Data):
    """
    Check initial conditions for this task, then submit an open_link_task and return the Task_ID
    """

    # Check Password
    if data.password != os.environ['DEFAULT_PASSWORD']:
        return ResponseModel(response="Incorrect Password")

    # Check Validity
    checkSheetNameValidity(data.category, data)
    if ((not data.isFolder) and (not data.isSheet)):
        logger.info("Folder or Sheet name does not exactly match category")
        response = "Folder or Sheet name does not exactly match category of submission destination. For example, if you are trying to submit something to the 'Therapist' sheet, there must also exist a 'Therapist' folder, with no trailing spaces"
        ResponseModel(response=response)

    # TODO Alter this to return the proper error if this function throws a flag
    # Set Variables
    setColumnVariables(data)

    # Write data to a file for use if adding candidates
    with open(SETTINGS_PATH, "w") as outfile:
        outfile.write(data.json())  # ( Not actually deprecated yet )
    logger.info("Successfully Set Column Variables")

    ################## Passed Pre-Checks ##################
    if data.action == "Text":
        # TODO move mail texts to task processor
        sendmailtexts(data)
        response = f"Successfully submitted Text Task with Task ID: \n{str(task)}\n(Disregard for now)"
        return ResponseModel(response=response)
    if data.action == "Add":
        # TODO New task process part
        task = open_link_task.apply_async(args=(data.dict(),), priority=5)
        response = f"Successfully submitted Add Candidate Task with Task ID: \n{str(task)}\n(Disregard for now)"
        return ResponseModel(response=response)

    return ResponseModel(response="Fell through to default response (Contact Victor)")


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

    # Concatonate dictionaries to send all info in one dict
    candidate_dict = candidateData.dict()

    # Submit Task Part 1/2
    result = process_candidate_part1.apply_async(
        args=(candidate_dict,), priority=1,)
    # Await Task Submission Confirmation
    result_output = result.wait(timeout=None, interval=0.5)

    # Log
    logger.info(f'{candidateData.name} - Add 1/2 Submitted')

    # Submit Finish Add Task
    result = process_candidate_part2.apply_async(
        args=(candidate_dict,), priority=2)
    # Await Task Submission Confirmation
    result_output = result.wait(timeout=None, interval=0.5)

    logger.info(f'{candidateData.name} - Add 2/2 Submitted')

    return {"message": "Success"}

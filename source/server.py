from auto_candidate import *
from paths import *
from worker import *

from pydantic import BaseModel
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
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


# Helper method to open a string in Chrome (Formatted for windows)
def openstring(data: Data):
    cmd = OPEN_CMD_LINK.format(data.link)  # Open link in chrome
    if os.system(cmd) == 0:
        logger.info(f"Successfully Opened Link: {data.link}")
    else:
        logger.info(f"Failed to open link: {data.link}")


class ResponseModel(BaseModel):
    response: str


@app.post('/submitformdata')
def submitformdata(data: Data):
    """
    Check initial conditions for this task, then submit an open_link_task and return the Task_ID
    """

    # Check Password
    if data.password != os.environ['DEFAULT_PASSWORD']:
        return ResponseModel(response="Incorrect Password")

    # Check Link length > 0
    if data.link is None or len(data.link) <= 0:
        return ResponseModel(response="No Link Provided")

    # TODO Alter this to return the proper error if this function throws a flag

    # Write settings data to file for use in adding candidates
    with open(SETTINGS_PATH, "w") as outfile:
        outfile.write(data.json())  # deprecated?
    logger.info("Successfully Set Group and Occupation")

    ################## Passed Pre-Checks ##################

    if data.action == "Add":
        # Submit task to open the submitted link
        task = open_link_task.apply_async(args=(data.dict(),), priority=5)
        response = f"\nSuccessfully Submitted Link\n\n Link: {data.link}\n\nGroup: {data.group}\n\nOccupation: {data.occupation}\n\nTask ID: {str(task)}"
        # Send Response
        return ResponseModel(response=response)

    # Default Response
    return ResponseModel(response="Fell through to default response (Contact Victor)")


@app.post('/submit_candidate')
async def submit_candidate(candidateData: candidateData):
    """
    Function called through userscripts to add candidate to db
    """

    # Make Pydantic Model Serializable
    candidate_dict = candidateData.dict()

    # Submit Task Part 1 (Part 2 is submitted by the worker)
    result = process_candidate_part1.apply_async(
        args=(candidate_dict,), priority=1,)

    return


@app.post('/submit_mailtext_test')
def submit_mailtext_test(data: Data):
    # Check Password
    if data.password != os.environ['DEFAULT_PASSWORD']:
        return ResponseModel(response="Incorrect Password")

    # Make Pydantic Model Serializable
    data_dict = data.dict()

    # Submit Test Text to Worker
    task = test_mailtext.apply_async(
        args=(data_dict,), priority=1,)

    # Create Response
    response = f"\nCreated Task for 'Test Mail/Text'\n\nTest Email: {data.test_email}\n\nTest Phone Number: {data.test_phone}\n\nTask ID: {str(task)}"

    return ResponseModel(response=response)


@app.post('/submit_mailtext')
def submit_mailtext(data: Data):

    # Check Password
    if data.password != os.environ['DEFAULT_PASSWORD']:
        return ResponseModel(response="Incorrect Password")

    # Make Pydantic Model Serializable
    data_dict = data.dict()

    # Submit Test Text to Worker
    task = send_group_mailtext.apply_async(
        args=(data_dict,), priority=1,)

    # Create Response
    response = f"\nSuccessfully Submitted Mail/Text Task\n\nSending Mail to Marked Candidates in Group: {data.group}\n\nTask ID: {str(task)}"

    return ResponseModel(response=response)

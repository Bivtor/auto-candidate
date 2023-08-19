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

# uvicorn server:app --reload
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


@app.post('/submitformdata')
def submitformdata(data: Data):
    """
    Check initial conditions for this task, then submit an open_link_task and return the Task_ID
    """

    # Check Password
    if data.password != os.environ['DEFAULT_PASSWORD']:
        return ResponseModel(response="Incorrect Password")
    if data.link is None or len(data.link) <= 0:
        return ResponseModel(response="No Link Provided")

    # TODO Alter this to return the proper error if this function throws a flag

    # TODO Set the occupation/group in settings

    # Write data to a file for use if adding candidates
    with open(SETTINGS_PATH, "w") as outfile:
        outfile.write(data.json())  # deprecated?
    logger.info("Successfully Set Group and Occupation")

    ################## Passed Pre-Checks ##################
    if data.action == "Text":
        # TODO move mail texts to task processor
        # TODO Re write send texts method
        response = f"Successfully submitted Text Task with Task ID: \n{str(task)}\n(Not currently working)"
        return ResponseModel(response=response)

    if data.action == "Add":
        # TODO New task process part
        task = open_link_task.apply_async(args=(data.dict(),), priority=5)
        response = f"\nSuccessfully Submitted Link\n\n Link: {data.link}\n\nGroup: {data.group}\n\nOccupation: {data.occupation}\n\nTask ID: {str(task)}"
        return ResponseModel(response=response)

    return ResponseModel(response="Fell through to default response (Contact Victor)")


@app.post('/submit_candidate')
async def submit_candidate(candidateData: candidateData):

    # Concatonate dictionaries to send all info in one dict
    candidate_dict = candidateData.dict()

    # Submit Task Part 1/2 ( part 2 is submitted by the worker )
    result = process_candidate_part1.apply_async(
        args=(candidate_dict,), priority=1,)

    # Await Task Submission Confirmation TODO remove this
    # result_output = result.wait(timeout=None, interval=0.5)

    # Log submission #TODO out of order ?
    # logger.info(f'{candidateData.name} - Add 1/2 Submitted')

    return


class MailData(BaseModel):
    message: dict


@app.post('/retrieve_email')
def createUsers(data: MailData):
    return 200

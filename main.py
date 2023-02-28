from auto_candidate import *

from pydantic import BaseModel
import os
import json
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
 
# This is 
@app.post('/test', response_model=ResponseModel)
def test():
    ##########################DO WORK##############################
    time.sleep(4)
    return ResponseModel(response="Finished Operation")



@app.post('/submitdata')
def submitdata(data: Data):
    # Check if operation is currently in progress
    f = open('isWorking.json')
    json_check=json.load(f)
    f.close()

    #If there is a current process, return checkModel with its"not_working_response"
    if json_check['isWorking']: return  ResponseModel(response="Operation Ongoing")

    #Set that there is now an operation ongoing since we passed the check
    json_check['isWorking'] = True
    with open("isWorking.json", "w") as outfile:
        json.dump(json_check, outfile)

    #Check Password
    # if sha256(data.password) != sha256(os.environ['DEFAULT_PASSWORD']): return "Incorrect Password"
    if data.password != os.environ['DEFAULT_PASSWORD']: return "Incorrect Password"

    # Check Validity
    checkSheetNameValidity(data.category, data)
    if((not data.isFolder) and (not data.isSheet)):
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

    #Stop Working
    json_check['isWorking'] = False
    with open("isWorking.json", "w") as outfile:
        json.dump(json_check,outfile)
        
    return ResponseModel(response="Success")

@app.post('/sendtexts')
def sendtexts():
    f = open('settings.json')
    data = json.load(f)
    sendmailtexts(data)
    f.close()
    return {"Success"}


# @app.post('/setparams')
# def setParams(data: params):
#     data = setColumnVariables(data)
#     with open("settings.json", "w") as outfile:
#         outfile.write(data.json())
    # return data

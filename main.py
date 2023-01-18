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


class openLink(BaseModel):
    link: str


class textData(BaseModel):
    category_texts: str


@app.post('/openstring')
def openstring(data: openLink):
    cmd = 'start chrome {}'.format(
        data.link[1:len(data.link)-1])  # OPEN chrome

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



@app.post('/submitdata')
def test(data: Data):

    #Check Password
    # if sha256(data.password) != sha256(os.environ['DEFAULT_PASSWORD']): return "Incorrect Password"
    if data.password != os.environ['DEFAULT_PASSWORD']: return "Incorrect Password"

    # Check Validity
    checkSheetNameValidity(data.category, data)
    if((not data.isFolder) and (not data.isSheet)):
        return "Folder or Sheet name does not exactly match category"
    
    # Set Variables
    setColumnVariables(data)
    with open("settings.json", "w") as outfile:
        outfile.write(data.json())
    print("success")

    ################## Passed Pre-Checks ##################
    if data.action == "Text":
        sendmailtexts(data)
    if data.action == "Add":
        pass

    return "Successs"

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

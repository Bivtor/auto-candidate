from auto_candidate import *

from pydantic import BaseModel
import os
import json
from fastapi import FastAPI


app = FastAPI()


class Data(BaseModel):
    hasResume: bool
    location: str
    name: str
    phone: str
    email: str
    date: str
    ziprecruiter: str


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
def createUsers(data: Data):
    global category
    create_candidate(data, category)
    print(data.name)
    return {"Success"}


@app.post('/sendtexts')
def sendtexts():
    f = open('settings.json')
    data = json.load(f)
    sendmailtexts(data)
    f.close()
    return {"Success"}


@app.post('/setparams')
def setParams(data: params):
    data = setColumnVariables(data)
    with open("settings.json", "w") as outfile:
        outfile.write(data.json())
    return data


class validate(BaseModel):
    sheetname: str


@app.post('/validatecategory', response_model=validData)
def validCategory(data: validate):
    return checkSheetNameValidity(data.sheetname)

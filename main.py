from auto_candidate import *

from typing import Union
from pydantic import BaseModel
import os
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

category = 'Pre-screening'
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
    category: str


class textData(BaseModel):
    category_texts: str
    start: int
    end: int


@app.post('/openstring')
def openstring(data: openLink):
    global category
    category = data.category
    print(data.link)
    print(category)

    cmd = 'start chrome {}'.format(
        data.link[1:len(data.link)-1])  # OPEN chrome

    # TODO This is broken I think, pretty sure returning false doesn't really do anything
    if os.system(cmd) != 0:
        return False


@app.post('/runfunction')
def createUsers(data: Data):
    global category
    create_candidate(data, category)
    print(data.name)
    return {"Success"}


@app.post('/sendtexts')
def sendtexts(data: textData):
    sendTwilioTexts(data.category_texts, data.start, data.end)
    return {"Success"}


@app.post('/validatecategory')
def validCategory(category: str):
    if checkSheetNameValidity(category):
        pass  # TODO return 200
    else:
        pass  # TODO return 500 or BAD


# flask run --host=0.0.0.0 to show to public

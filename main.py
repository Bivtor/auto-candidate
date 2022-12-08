from auto_candidate import *

from pydantic import BaseModel
import os
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

category = 'Pre-screening'
sheetId = '0'  # Pre-screening
folderId = '1YFkV8Tfm9WwR5Xb_aWaKHjP2k3weghEJ'  # Misc

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


@app.post('/validatecategory', response_model=validData)
def validCategory(data: validData):
    return checkSheetNameValidity(sheetname)

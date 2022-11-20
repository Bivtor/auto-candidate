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

class inputs(BaseModel):
    link: str
    category: str

@app.post('/openstring')
def openstring(data: inputs):
    global category 
    category = data.category
    print(data.link)
    print(category)

    cmd = 'start chrome {}'.format(data.link[1:len(data.link)-2])
    if os.system(cmd) != 0: #TODO This is broken I think, pretty sure returning false doesn't really do anything
        return False
    

@app.post('/runfunction')
def createUsers(data: Data):
    global category
    create_candidate(data, category)
    print(data.name)
    return {"success"}


# flask run --host=0.0.0.0 to show to public

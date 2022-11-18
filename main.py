from auto_candidate import *

from typing import Union
from pydantic import BaseModel
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


@app.post('/runfunction')
def createUsers(data: Data):
    create_Therapist(data)
    print(data.name)

    return {"success"}


# flask run --host=0.0.0.0 to show to public

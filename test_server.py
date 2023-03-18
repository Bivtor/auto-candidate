from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:3000",
# ]


class Data(BaseModel):
    cmd: str


@app.post('/')
def createUsers(data: Data):
    print(data.cmd)
    with open('output.txt', 'a') as f:
        f.write(data.cmd)
        f.write("\n")



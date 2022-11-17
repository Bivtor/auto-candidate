from flask import Flask
from flask import request
# from './auto-candidate' import *
import os

app = Flask(__name__)


@app.route('/runfunction', methods=['GET', 'POST'])
def runfunction():
    if request.method == 'GET':
        os.system("python3 auto-candidate.py")
    return "<div> Listed ls in terminal </div>"


# flask run --host=0.0.0.0 to show to public

import os
import re
from dotenv import load_dotenv
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from pydantic import BaseModel, Field

load_dotenv()
# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.event("app_mention")
def event_test(event, say):
    text = event['text']
    inputlist = re.sub(' +', ' ', text[text.find('>')+2:].strip()).split(' ')
    if len(inputlist) < 0:
        return
    method = inputlist[0]
    match method:
        case 'add':
            link = inputlist[1]
            category = " ".join(inputlist[2:])

            # Validate Category and Set Params
            valid = validateCategory(category)
            say(valid.get('message', "Failed to validate category"))  # Say message
            if not valid['continue']:
                return

            # Open String
            openstring = requests.post(url='http://127.0.0.1:8000/openstring', headers={
                'accept': 'application/json', 'Content-Type': 'application/json'}, json={'link': link})

            print(openstring)

            say("Inputting Candidates in the {} Category".format(category))

        case 'text':
            category = " ".join(inputlist[1:])

            # Validate Category
            valid = validateCategory(category)
            say(valid.get('message', "Failed to validate category"))  # Say message
            if not valid['continue']:
                return
            # Send Text Messages
            say("Starting to send texts in the {} Category".format(category))
            requests.post(url='http://127.0.0.1:8000/sendtexts', headers={
                'accept': 'application/json', 'Content-Type': 'application/json'}, json={})
            say("Finished")


def validateCategory(category: str):
    r = requests.post(url='http://127.0.0.1:8000/validatecategory', headers={
        'accept': 'application/json', 'Content-Type': 'application/json'}, json={'sheetname': category}).json()

    r['category'] = category

    if (r['isSheet'] and r['isFolder']):
        r['message'] = "Successfully Validated {} category".format(category)
        r['continue'] = True
    else:
        r['message'] = "Unable to find a corresponding Folder and Sheet for the {} category\nFound Sheet: {}\nFound Folder: {}".format(
            category, r['isSheet'], r['isFolder'])
        r['continue'] = False
        return r

    # Set Parameters and update r val
    r.update(requests.post(url='http://127.0.0.1:8000/setparams', headers={'accept': 'application/json', 'Content-Type': 'application/json'}, json={
        'sheetId': r['sheetId'], 'folderId': r['folderId'], 'category': category}).json())
    if r.get('err'):  # If there is an error, update the message that will be printed
        print("Found an error")
        r['message'] = r['err']
        r['continue'] = False

    return r


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

import os
import re
from dotenv import load_dotenv
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
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
            category = inputlist[2]
            print(requests.post(url='http://127.0.0.1:8000/openstring', headers={
                  'accept': 'application/json', 'Content-Type': 'application/json'}, json={'link': link, 'category': category}))
            say("Inputting Candidates in the {} Category".format(category))
        case 'text':
            category = inputlist[1]
            start = 2
            end = 998
            # if includes
            if len(inputlist) > 2:
                start = inputlist[2]
            if len(inputlist) > 3:
                end = inputlist[3]
            requests.post(url='http://127.0.0.1:8000/sendtexts', headers={
                'accept': 'application/json', 'Content-Type': 'application/json'}, json={'category_texts': category, 'start': start, 'end': end})
            say("Sending Texts to Candidates in the {} Category from rows {} to {}".format(
                category, start, end))


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

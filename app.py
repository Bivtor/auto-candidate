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
            category = " ".join(inputlist[2:])
            # TODO Validate Category
            resp = requests.post(url='http://127.0.0.1:8000/validatecategory', headers={
                                 'accept': 'application/json', 'Content-Type': 'application/json'}, json={'sheetname': category})

            print(resp)
            return

            # Add cateory validation here
            print(requests.post(url='http://127.0.0.1:8000/openstring', headers={
                  'accept': 'application/json', 'Content-Type': 'application/json'}, json={'link': link, 'category': category}))
            say("Inputting Candidates in the {} Category".format(category))

        case 'text':
            category = " ".join(inputlist[1:])
            # TODO Validate Category

            start = 2
            end = 998

            requests.post(url='http://127.0.0.1:8000/sendtexts', headers={
                'accept': 'application/json', 'Content-Type': 'application/json'}, json={'category_texts': category, 'start': start, 'end': end})
            say("Sending Texts to Candidates in the {} Category".format(
                category))


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

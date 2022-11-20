import os
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
    link = text[text.find('>')+2:]
    category = link[link.find(' ')+1:]
    link = link[:link.find(' ')+1]

    re = requests.post(url='http://127.0.0.1:8000/openstring', headers={'accept': 'application/json', 'Content-Type': 'application/json'}, json={'link': link, 'category': category})
    if str(re) == '<Response [200]>':
        say("Successfully Submitted link, inputting data!")
    else:
        say("Unsuccessful Link submission")

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()



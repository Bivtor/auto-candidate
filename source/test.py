import os
import os.path
from auto_candidate import *


def publish():
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    if os.path.exists('creds/token.json'):
        creds = Credentials.from_authorized_user_file(
            'creds/token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds/credentials2.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('creds/token.json', 'w') as token:
            token.write(creds.to_json())

    # Try
    try:
        gmail = build('gmail', 'v1', credentials=creds)
        request = {
            'labelIds': ['INBOX', 'SPAM'],
            'topicName': 'projects/auto-candidate-365121/topics/my_topic'
        }
        response = gmail.users().watch(userId='me', body=request).execute()
        print(response)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')



def main():
    publish()


if __name__ == "__main__":
    main()
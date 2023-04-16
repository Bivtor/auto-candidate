from auto_candidate import build, HttpError, creds


def publish():
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

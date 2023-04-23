import re
import os
import json
import base64
from dotenv import load_dotenv


from auto_candidate import DEFAULT_SHEET_DEST,JOBMAP_PATH,SPREADSHEET_ID, NAMES_PATH,creds, build, HttpError, Data, SETTINGS_PATH, logger, WORKING_PATH, ENV_PATH
from auto_candidate import checkSheetNameValidity, setColumnVariables, setWorking, checkWorking

load_dotenv(dotenv_path=ENV_PATH)


def getRawDataInfo(raw_message: str) -> dict:
    """
    returns a dict object with the candide info we need with the keys:
        candidate_name
        candidate_url
        sheet_destination

        Only call this function after using checkIsCandidateSubmissionNotice()
    """
    results:dict = {}

    def replace_whitespace(string):
        # Replace all non-space white space characters with spaces
        string = ' '.join(string.split())
        return string

    # Get URL
    pattern = r'https://www\.ziprecruiter\.com/contact/response/[^/]*/[^/]*\?'
    match = re.search(pattern, raw_message)
    candidate_url = match.group(0)
    results['candidate_url'] = candidate_url
    logger.info(f'Got URL : {candidate_url}')

    # Get candidate name
    loc = raw_message.find("New Candidate:")
    candidate_name = raw_message[loc+15:loc+100]
    candidate_name = candidate_name[:candidate_name.find(
        "for")].strip()
    candidate_name = replace_whitespace(candidate_name)
    results['candidate_name'] = candidate_name
    logger.info(f'Got Name : {candidate_name}')

    # Get job title
    job_title_area_location = raw_message.find("New Candidate:")
    job_title = raw_message[job_title_area_location:job_title_area_location+100]
    job_title = job_title[job_title.find("'")+1:]
    job_title = job_title[:job_title.find("'")].lower().strip()
    job_title = replace_whitespace(job_title)
    logger.info(f'Got Job Title : {job_title}')
    
    # Get sheet destination based on job title
    sheet_destination = handleJobTitle(job_posting_title=job_title)
    results['sheet_destination'] = sheet_destination
    # Result logged in function

    return results


def handleJobTitle(job_posting_title: str) -> str:
    """
        Converts the job posting title to the title of a sheet destination that is in the google sheets
    """
    logger.info('Attempting to retrieve sheet destination')

    # Create checkExistence function to be used 
    def checkLocalExistence(data: dict) -> str:
        if job_posting_title in data:
            logger.info(f'Found appropriate sheet destination: {data[job_posting_title]}')
            return data[job_posting_title]
        else:
            logger.info(f'Could not find appropriate sheet desination: {DEFAULT_SHEET_DEST}')
            return DEFAULT_SHEET_DEST
        
    if os.path.isfile(JOBMAP_PATH):
        # If it exists open it
        with open(JOBMAP_PATH, 'r') as f:
            data = json.load(f) # Load data
            return checkLocalExistence(data) # Check if the sheet_name exists in the json
    else:
        # If file does not exist, create it
        logger.info(f'Could not find \'{JOBMAP_PATH}\', creating one (This must be filled in by hand)') 
        
        with open(JOBMAP_PATH, 'w') as f:
            json.dump({}, f)
        
        # Log creation of file and return default
        logger.info(f'Returning default sheet_destination {DEFAULT_SHEET_DEST}') 
        return DEFAULT_SHEET_DEST


def process_message():
    try:
        service = build('gmail', 'v1', credentials=creds)

        # Get list of last (1) message ID's
        messages = service.users().messages().list(
            userId='me', maxResults=1).execute()

        # Get ID of last message
        message = messages['messages'][0]['id']

        # Get raw_data of last message (Becasue the raw data contains the url we want and not the non raw for some reason)
        message = service.users().messages().get(
            userId='me', id=message, format='raw').execute()

        # Decode raw_data
        raw_message = base64.urlsafe_b64decode(
            message['raw'].encode('utf-8')).decode('utf-8')
        
        # Log
        logger.info('Checking most recent email')
        
        # Check if is the right email (ZR Notification)
        
        if not checkIsCandidateSubmissionNotice(raw_message=raw_message): 
            logger.info('Notification was not for candidate submission, returning\n')
            return 200

        # Log
        logger.info('Notification was for candidate submission, gathering data')

        # Gather data from email before checking if candidate exists
        parsed_email_data:dict = getRawDataInfo(raw_message=raw_message)
        
        # Extract data from dict
        candidate_url = parsed_email_data['candidate_url']
        candidate_name = parsed_email_data['candidate_name']
        sheet_destination = parsed_email_data['sheet_destination']

        # Check if candidate already exists
        if checkCandidateExistence(SPREADSHEET_ID, sheet_name=sheet_destination, name=candidate_name):
            logger.info('Candidate already exists, returning')
            return 200
        
        # We know the candidate is not in the spreadsheet, add the candidate (updates json at end of function)
        logger.info(f'Candidate is new, Now adding to them to the {sheet_destination} sheet')

        # Call clone of submit data (checks password, isRunning, columnVariables, etc)
        final_candidate_data = Data(action='Add', category=sheet_destination,
                        link=candidate_url, password='g&c2023', message="")

        submitdata_clone(data=final_candidate_data)  # Add Candidate

        logger.info('Submitted to spreadsheet, check results')

        # TODO def sendAWSEmail(name: str, email: str, body: str, category: str, mailsender):
        # TODO Alert Victor of additon

        # TODO Get the last line of the spreadsheet
        # TODO Call the send text function for only the last line of the spreadsheet

    except HttpError as error:
        print(f'An error occurred: {error}')


def checkIsCandidateSubmissionNotice(raw_message: str)-> bool:
    # Check if the text contains a URL in the format "https://www.ziprecruiter.com/contact/response/*/*"
    pattern = r'https://www\.ziprecruiter\.com/contact/response/[^/]*/[^/]*\?'
    match = re.search(pattern, raw_message)
    if match: 
        
        return True
    else: 
        return False


def checkCandidateExistence(spreadsheet_id, sheet_name, name) -> True:
    """
    Check if the candidate already exists in the spreadsheet, in the spreadsheet, we only call this function if the top 
    email is a notification of a new candidate, and we use this function to prevent unnecessary calls to the API by using a local
    storage of the names, and only calling the API if we have to (ie when the job sheet does not exist locally)

    We update the local file every time a new request is made, so updates are only called from here if the sheet does not exist
    """

    # Check if file exists
    if os.path.isfile(NAMES_PATH):
        # If it exists open it
        with open(NAMES_PATH, 'r') as f:
            data = json.load(f)

            # Check if the sheet_name exists in the json
            if sheet_name in data:
                if name in data[sheet_name]:  # Return True if we find the name in the file
                    return True
                else:
                    return False
            # Update the spreadsheet if we can't find the name the sheet_name
            else:
                updateCandidateExistence(
                    spreadsheet_id=spreadsheet_id, sheet_name=sheet_name)
                with open(NAMES_PATH, 'r') as f:
                    data = json.load(f)
                    # Try to find the name again
                    # Return True if we find the name in the file
                    if name in data[sheet_name]:
                        return True
                    else:
                        return False
    # If file does not exist
    else:
        # Create file
        with open(NAMES_PATH, 'w') as f:
            json.dump({}, f)

        # Update the file
        updateCandidateExistence(
            spreadsheet_id=spreadsheet_id, sheet_name=sheet_name)

        # Try to find the name again
        with open(NAMES_PATH, 'r') as f:
            data = json.load(f)
            if name in data[sheet_name]:  # Return True if we find the name in the file
                return True
            else:
                return False


def updateCandidateExistence(spreadsheet_id, sheet_name):
    try:
        # Authorize with Google Sheets API
        service = build('sheets', 'v4', credentials=creds)

        # Get the values in the column
        RANGE = f"{sheet_name}!A:A"

        # Execute request
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=RANGE).execute()

        # Get values
        column_values = result.get("values", [])

        # Remove arbirary list within list
        column_values = [val for sublist in column_values for val in sublist]

        # Update the value in the json file
        with open(NAMES_PATH, "r") as f:
            data = json.load(f)

        data[sheet_name] = column_values

        with open(NAMES_PATH, 'w') as f:
            json.dump(data, f, indent=4)

    except HttpError as error:
        print(F'An error occurred: {error}')


def submitdata_clone(data: Data):
    # Check if operation is currently in progress
    if checkWorking():
        logger.info("Request made whilst currently working on something else -> Could not proceed")
        return 200
    
    # Set that there is now an operation ongoing since we passed the check
    setWorking(True)

    # Check Password
    if data.password != os.environ['DEFAULT_PASSWORD']:
        logger.info("Wrong Password, returning")
        setWorking(False)
        return {"message":"Incorrect Password"}

    # Check Validity
    checkSheetNameValidity(data.category, data)
    if ((not data.isFolder) and (not data.isSheet)):
        logger.info("Incorrect params in checkSheetNameValidity function, returning")
        setWorking(False)
        return {"message":"Folder or Sheet name does not exactly match category"}

    # Set Variables
    setColumnVariables(data)

    # Write data to a file for use if adding candidates
    with open(SETTINGS_PATH, "w") as outfile:
        outfile.write(data.json())
    logger.info("Successfully set Spreadsheet Column Variables")

    ################## Passed Pre-Checks ##################
    if data.action == "Add":
        logger.info("Calling open string function")
        openstring_clone(data)

    # Stop Working
    setWorking(False)

    # return a value
    return 200

def openstring_clone(data: Data):
    logger.info("Opening Link: {}".format(data.link))
    cmd = 'start chrome {}'.format(data.link)  # OPEN chrome
    if os.system(cmd) != 0:
        return False


def decideTokenRefresh(path: str):
    # Load JSON data from file path
    with open(path, 'r') as f:
        data = json.load(f)
        
    # Check if shouldUpdate mod 5 == 0
    if data['shouldUpdate'] % 5 == 0:
        # Call publish function if condition is true
        logger.info("Decided to refresh Gmail token")
        pushMailToUs()
        
    # Increment shouldUpdate by 1
    data['shouldUpdate'] += 1
    
    # Update the JSON file with the new value of shouldUpdate
    with open(path, 'w') as f:
        json.dump(data, f)
    
def pushMailToUs():
    try:
        gmail = build('gmail', 'v1', credentials=creds)
        request = {
            'labelIds': ['INBOX', 'SPAM'],
            'topicName': 'projects/auto-candidate-365121/topics/my_topic'
        }
        response = gmail.users().watch(userId='me', body=request).execute()
        logger.info(f"Successfully refreshed gmail token: {response}")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        logger.info(f'An error occurred when trying to refresh gmail token: {error}')


def main():
    print("test")

if __name__ == '__main__':
    main()


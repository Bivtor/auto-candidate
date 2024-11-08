from base import *
from dotenv import load_dotenv
import csv
import json
import requests
import os
from fuzzywuzzy import fuzz
from occupation_detection import getOccupationWrapper
load_dotenv(dotenv_path=ENV_PATH)


def main():
    logger.info('--------------------------------------------- Starting Correction Algorithm ---------------------------------------------')
    """
    Short script to go through candidates with the default label, get their global ID, and do a better check for a resume from the folder

    1. 
    get defaults from monday

    2. 
    get matching ID from candidate.csv

    3.
    get matching Global ID from resume.csv

    4.
    get matching resume file (file should CONTAIN the id returned, not exactly match it)

    5.
    Upload it if its a pdf

    6.
    Ask chatgpt for the occupation based on this resume

    7. 
    Update the occupation field
    """

    default_names = getDefaultOccupationCandidatesFromMonday()

    for idx, person in enumerate(default_names):

        name: str = person['name']
        monday_id: str = person['id']
        logger.info(
            f'---------------------------------------------#{idx} {name}---------------------------------------------\n')

        # Get Row
        row = find_matching_row_candidate(
            name, CANDIDATE_CSV_PATH)  # Uses fuzzy wuzz

        # Decide if we move on
        if row is None:
            logger.info('No candidate row found')
            continue

        row_fname = row['FIRSTNAME']
        row_lname = row['LASTNAME']
        row_id = row['ID']
        logger.info(
            f'Found matching name: {name} matched to {row_fname}, {row_lname}, #{row_id}')

        # Get global ID
        # Skipping this step because the global id is not always correct, but the candidate ID is always a part of the global id
        # .... Great work there jobdiva...
        # global_id = find_global_id(RESUME_CSV_PATH, row_id)

        # Find a matching resume (Which should exist )
        file_path = find_file(RESUME_FOLDER_PATH, row_id)
        if file_path is None:
            logger.info('No resume found')
            continue
        logger.info(f'Got matching file for {name} : {file_path}')

        # Upload newfound resume
        uploadCandidateResume(monday_id, file_path)

        # Get Occupation
        occupation_dict = getOccupationWrapper(file_path, None)
        occupation_name = occupation_dict['name']
        occupation_id = occupation_dict['id']
        logger.info(f'Got occupation: {occupation_name}')

        # Update occupation
        updateMondayOccupation(monday_id, occupation_id)

        # Testing
        if idx > 300:
            logger.info('done')
            return


def find_global_id(csv_file_path, search_id):
    # Open the CSV file
    with open(csv_file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)

        # Iterate through each row to find the matching ID
        for row in reader:
            if row['CANDIDATEID'] == search_id:
                # Return the GLOBABLID of the matching row
                return row['GLOBAL_ID']

    # Return None if no matching ID is found
    return None


def find_matching_row_candidate(input_name, csv_file_path, threshold=80):
    # Open the CSV file
    with open(csv_file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)

        # Iterate through each row in the CSV
        for row in reader:
            # Concatenate the FIRSTNAME and LASTNAME
            full_name = f"{row['FIRSTNAME']} {row['LASTNAME']}"

            # Calculate the match score
            match_score = fuzz.ratio(full_name, input_name)

            # Check if match score meets the threshold
            if match_score >= threshold:
                return row  # Return the row if a match is found

    # Return None if no match is found
    return None


def find_file(directory, file_name):
    # Iterate through files in the given directory
    for file in os.listdir(directory):
        # Check if the file is a PDF and contains the file_name substring
        if file_name in file and (file.endswith('.pdf') or file.endswith('.docx')):
            # Return the full path to the first matching PDF file
            return os.path.join(directory, file)

    # Return None if no matching PDF file is found
    return None


def getDefaultOccupationCandidatesFromMonday() -> list:
    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    headers = {
        "Authorization": apiKey,
        "API-version": "2024-10"
    }
    url = "https://api.monday.com/v2"

    # Generate Query
    # TODO Add code that defaults to fail if we cannot find the proper group id
    q = f"""
        {{items_page_by_column_values (limit: 500,board_id: {BOARD_ID}, columns: [{{column_id: "occupation__1", column_values: [\"default\"]}}]) {{
                items{{
                    name
                    id
                }}
            }}
        }}
        """

    # Send request
    response = requests.post(url=url, headers=headers, json={'query': q})

    # Handle response
    if response.status_code == 200:
        # Extract data
        response_data = response.json()
        response_list = response_data['data']['items_page_by_column_values']['items']
        return response_list
        # Log
        # logger.info(f"{name} - Successfully got info from monday")
    else:
        # Handle get info fail
        logger.info(
            f"Failed to get list from Monday")
        return []


def uploadCandidateResume(monday_id: str, f: str):

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    headers = {"Authorization": apiKey, 'API-version': '2024-04'}
    url = "https://api.monday.com/v2/file"

    payload = {
        'query': f'mutation add_file($file: File!) {{add_file_to_column (item_id: {monday_id}, column_id:"files" file: $file) {{id}}}}',
        'map': '{"image":"variables.file"}'
    }

    file_name = os.path.basename(f)

    files = [
        ('image', (file_name, open(f, 'rb'), 'application/octet-stream'))
    ]

    # logger.info(payload)

    # Send Request
    response = requests.post(url, headers=headers, data=payload, files=files)

    # Handle response
    response_data = response.json()
    if response.status_code == 200:
        logger.info("Successfully uploaded Resume")
        # logger.info(f"Response: {response_data}")
    else:
        logger.error(f"Response: {response_data}")
        logger.error("Failed to upload Resume")
        raise Exception('resume upload fail')

    return


def updateMondayOccupation(monday_id, new_occupation_id):
    """
    Updates item of monday item based on a pre-determined item ID
    """

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey, "API-version": "2023-04"}

    # Assign Column values if found
    column_values = {
        "occupation__1": str(new_occupation_id),
    }

    # Format column_values
    j = json.dumps(column_values)
    j = j.replace('"', '\\\"')

    # Generate mutation
    createItemMutation = f'''mutation {{
        change_multiple_column_values (
            item_id: {monday_id}
            board_id: {BOARD_ID}
            column_values : "{j}") {{id}}
            }}
            '''
    d = {"query": createItemMutation}

    # Send mutation
    response = requests.post(url=apiUrl, json=d, headers=headers)

    # Handle response
    if response.status_code == 200:
        response_data = response.json()
        new_id = response_data['data']['change_multiple_column_values']['id']
        logger.info(
            f"Updated occupation to {new_occupation_id}")
    else:
        logger.info("Failed to update occupation")

    return


if __name__ == '__main__':
    main()

from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv
from base import get_raw_text, logger


ENV_PATH = '../../.env'

load_dotenv(dotenv_path=ENV_PATH)

label_mapping = {
    'VOB': 0,
    'MRA': 1,
    'RN': 2,
    'Therapist': 3,
    'UR': 4,
    'Nutritionist/Dietician': 5,
    'EA': 6,
    'Event Planner': 7,
    'BD/Admissions': 8,
    'Jr. Recruiter': 9,
    'Recruiter': 10,
    'RADT/CADC/Tech': 11,
    'Med Office Admin': 12,
    'Podcast Producer': 13,
    'Front Desk Receptionist': 14,
    'Surgical Tech': 15,
    'Aesthetic Nurse': 16,
    'EMT': 17,
    'Occupational Therapist': 18,
    'LVN': 19,
    'CNA': 101,
    'Chef': 102,
    'MRA/Biller': 103,
    'Physical Therapist': 104,
    'Nurse': 105,
    'Medical Director': 106,
    'Medical Records Assistant': 107,
    'Specimen Processor': 108,
    'Infection Preventionist': 109,
    'Medical Technologist': 110,
    'Admin': 151,
    'HR': 152,
    'Nurse Practioner': 153,
    'Director of Nursing': 154,
    'CRNA': 155,
    'Program and Clinical Director': 157,
    'CADC': 158,
    'Clinical Director': 159,
    'Program Director': 160,
    'Default': 156
}


def clean_text(text):
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    # Regex pattern: Match sequences of single letters separated by spaces (e.g., "m e r d e s i r e s")
    corrected_text = re.sub(
        r'(\b\w)( \w\b)+', lambda m: m.group(0).replace(" ", ""), text)

    return corrected_text


def getOccupation(text: str) -> str:
    # Define client
    client = OpenAI(
        # organization='proj_lLpwDwIe3dHJj8a4XaY7DAq4',
        # project='proj_lLpwDwIe3dHJj8a4XaY7DAq4',
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    # Get response
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "Given this list of pairs:\n\n\"labels\": [\n    { \"name\": \"VOB\", \"id\": 1 },\n    { \"name\": \"MRA\", \"id\": 2 },\n    { \"name\": \"RN\", \"id\": 3 },\n    { \"name\": \"Therapist\", \"id\": 4 },\n    { \"name\": \"UR\", \"id\": 5 },\n    { \"name\": \"Nutritionist/Dietician\", \"id\": 6 },\n    { \"name\": \"EA\", \"id\": 7 },\n    { \"name\": \"Event Planner\", \"id\": 8 },\n    { \"name\": \"BD/Admissions\", \"id\": 9 },\n    { \"name\": \"Jr. Recruiter\", \"id\": 10 },\n    { \"name\": \"Recruiter\", \"id\": 11 },\n    { \"name\": \"RADT/CADC/Tech\", \"id\": 12 },\n    { \"name\": \"Med Office Admin\", \"id\": 13 },\n    { \"name\": \"Podcast Producer\", \"id\": 14 },\n    { \"name\": \"Front Desk Receptionist\", \"id\": 15 },\n    { \"name\": \"Surgical Tech\", \"id\": 16 },\n    { \"name\": \"Aesthetic Nurse\", \"id\": 17 },\n    { \"name\": \"EMT\", \"id\": 18 },\n    { \"name\": \"Occupational Therapist\", \"id\": 19 },\n    { \"name\": \"LVN\", \"id\": 20 },\n    { \"name\": \"CNA\", \"id\": 102 },\n    { \"name\": \"Chef\", \"id\": 103 },\n    { \"name\": \"MRA/Biller\", \"id\": 104 },\n    { \"name\": \"Physical Therapist\", \"id\": 105 },\n    { \"name\": \"Nurse\", \"id\": 106 },\n    { \"name\": \"Medical Director\", \"id\": 107 },\n    { \"name\": \"Medical Records Assistant\", \"id\": 108 },\n    { \"name\": \"Specimen Processor\", \"id\": 109 },\n    { \"name\": \"Infection Preventionist\", \"id\": 110 },\n    { \"name\": \"Medical Technologist\", \"id\": 111 },\n    { \"name\": \"Admin\", \"id\": 152 },\n    { \"name\": \"HR\", \"id\": 153 },\n    { \"name\": \"Nurse Practitioner\", \"id\": 154 },\n    { \"name\": \"Director of Nursing\", \"id\": 155 },\n    { \"name\": \"CRNA\", \"id\": 156 },\n   { \"name\": \"Program and Clinical Director\", \"id\": 158 },\n    { \"name\": \"CADC\", \"id\": 159 },\n    { \"name\": \"Clinical Director\", \"id\": 160 },\n    { \"name\": \"Program Director\", \"id\": 161 },\n    { \"id\": 162, \"name\": \"Social Worker\" },\n  ],\n\nOf these jobs, which one do you think this person was applying for given the inputted text from their resume, return a json object \n\nThe json object should be of the format {\"id\": [ID], \"name\": [job_name]} and must exactly match one of the options I have provided\n\nThe text from their resume is as follows:\n\n" + text
                        }
                    ]
                }
            ],
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_object"
            }
        )

        # Access the JSON response
        json_response = response.model_dump(
        )['choices'][0]['message']['content']

        # Convert the JSON string into a Python dictionary
        try:
            data = json.loads(json_response)
            return data  # Return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return 'Default'  # Return default

    except Exception as e:
        print(f"Exception getting data:\n{e}")
        return 'Default'


def getOccupationWrapper(resume_location: str | None, notes: str | None) -> dict:
    """
    Get the occupation from gpt-4o-mini

    return an dict object containing:
        name
        id
    """

    # Check that resume location exists
    if resume_location is not None:
        text = get_raw_text(resume_location)

        text = clean_text(text)

        # Query gpt
        occupation_object = getOccupation(text)

        # extract
        occupation_name = occupation_object.get('name', "name")
        occupation_id = occupation_object.get('id', "id")

        logger.info(
            f'Detected Occupation: {occupation_name} : {occupation_id}')

        # return
        return occupation_object

    # Try to infer position based on notes if no resume exists
    # elif notes is not None:
    #     # Query gpt
    #     try:
    #         occupation_title = getOccupation(notes)['job']

    #         # Set to result of gpt, or default if request fails
    #         occupation_id = label_mapping.get(occupation_title, 156)

    #         # Log
    #         logger.info(
    #             f'Resume not found, but notes exist, inferred: {occupation_title} : {occupation_id} from notes')

    #         return {
    #             "occupation_title": occupation_title,
    #             "occupation_id": occupation_id
    #         }
    #     except Exception as e:
    #         # Log
    #         logger.error(f'Error while asking gpt-4o-mini for job: {e}')
    #         logger.error(f'Setting occupation to 156 (default): {e}')

    #         # Set defaults
    #         occupation_title = "Default"
    #         occupation_id = 156

    #         # Log
    #         return {
    #             "occupation_title": occupation_title,
    #             "occupation_id": occupation_id
    #         }

    # If no notes and no resume, assign defaults
    else:
        # Set defaults
        occupation_title = "default"
        occupation_id = 157

        # Log
        logger.info(
            f'Resume not found, Notes not found, assigning default occupation: {occupation_title} : {occupation_id} from notes')
        return {
            "name": occupation_title,
            "id": occupation_id
        }

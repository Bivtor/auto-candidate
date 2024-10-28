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
                            "text": "of these 37 jobs:\n    id_to_label_mapping = {{\n        0: 'VOB',\n        1: 'MRA',\n        2: 'RN',\n        3: 'Therapist',\n        4: 'UR',\n        5: 'Nutritionist/Dietician',\n        6: 'EA',\n        7: 'Event Planner',\n        8: 'BD/Admissions',\n        9: 'Jr. Recruiter',\n        10: 'Recruiter',\n        11: 'RADT/CADC/Tech',\n        12: 'Med Office Admin',\n        13: 'Podcast Producer',\n        14: 'Front Desk Receptionist',\n        15: 'Surgical Tech',\n        16: 'Aesthetic Nurse',\n        17: 'EMT',\n        18: 'Occupational Therapist',\n        19: 'LVN',\n        101: 'CNA',\n        102: 'Chef',\n        103: 'MRA/Biller',\n        104: 'Physical Therapist',\n        105: 'Nurse',\n        106: 'Medical Director',\n        107: 'Medical Records Assistant',\n        108: 'Specimen Processor',\n        109: 'Infection Preventionist',\n        110: 'Medical Technologist',\n        151: 'Admin',\n        152: 'HR',\n        153: 'Nurse Practioner',\n        154: 'Director of Nursing',\n        155: 'CRNA',\n        157: 'Program and Clinical Director',\n        158: 'CADC',\n        159: 'Clinical Director',\n        160: 'Program Director'\n    }}\n\n    Of these 37 jobs, which one do you think this person was applying for given the inputted text from their resume, return a json object with job: JOB_SELECTION, The text you return must exactly match the text from one of the options I provided you\n\n" + text,
                            "type": "text"
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
            return data['job']  # Return data
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
        occupation_title
        occupation_id
    """

    # Check that resume location exists
    if resume_location is not None:
        text = get_raw_text(resume_location)

        text = clean_text(text)

        # Query gpt
        occupation_title = getOccupation(text)
        # Set to result of gpt, or default if request fails
        occupation_id = label_mapping.get(occupation_title, 156)

        logger.info(
            f'Detected Occupation: {occupation_title} : {occupation_id}')

        return {
            "occupation_title": occupation_title,
            "occupation_id": occupation_id
        }

    # Try to infer position based on notes if no resume exists
    elif notes is not None:
        # Query gpt
        try:
            occupation_title = getOccupation(notes)['job']

            # Set to result of gpt, or default if request fails
            occupation_id = label_mapping.get(occupation_title, 156)

            # Log
            logger.info(
                f'Resume not found, but notes exist, inferred: {occupation_title} : {occupation_id} from notes')

            return {
                "occupation_title": occupation_title,
                "occupation_id": occupation_id
            }
        except Exception as e:
            # Log
            logger.error(f'Error while asking gpt-4o-mini for job: {e}')
            logger.error(f'Setting occupation to 156 (default): {e}')

            # Set defaults
            occupation_title = "Default"
            occupation_id = 156

            # Log
            return {
                "occupation_title": occupation_title,
                "occupation_id": occupation_id
            }

    # If no notes and no resume, assign defaults
    else:
        # Set defaults
        occupation_title = "Default"
        occupation_id = 156

        # Log
        logger.info(
            f'Resume not found, Notes not found, assigning default occupation: {occupation_title} : {occupation_id} from notes')
        return {
            "occupation_title": occupation_title,
            "occupation_id": occupation_id
        }

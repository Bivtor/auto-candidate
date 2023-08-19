import requests
import os
import json
import re
import glob
from dotenv import load_dotenv
from paths import ENV_PATH, SETTINGS_PATH, DOWNLOAD_PATH
from auto_candidate import candidateData, logger

load_dotenv(dotenv_path=ENV_PATH)

BOARD_ID = 4846750007
DEFAULT_GROUP = '1690065138_recruiting_pre_scre'  # Miscellaneous
GROUP_ID_MAP = {
    "groups": [
        {
            "id": "1690064031_recruiting_pre_scre",
            "title": "Therapist"
        },
        {
            "id": "1690063283_recruiting_pre_scre",
            "title": "Nurse"
        },
        {
            "id": "1690061481_recruiting_pre_scre",
            "title": "Surgical Tech"
        },
        {
            "id": "1690061214_recruiting_pre_scre",
            "title": "Front Desk Receptionist"
        },
        {
            "id": "1690060744_recruiting_pre_scre",
            "title": "Podcast Producers"
        },
        {
            "id": "1690060445_recruiting_pre_scre",
            "title": "Med Office Admin"
        },
        {
            "id": "1690059997_recruiting_pre_scre",
            "title": "RADT/CADC/Tech"
        },
        {
            "id": "1690059373_recruiting_pre_scre",
            "title": "Recruiter"
        },
        {
            "id": "1690057610_recruiting_pre_scre",
            "title": "BD/Admissions"
        },
        {
            "id": "1690054853_recruiting_pre_scre",
            "title": "Event Planner"
        },
        {
            "id": "1690054322_recruiting_pre_scre",
            "title": "EA"
        },
        {
            "id": "1690054026_recruiting_pre_scre",
            "title": "VOB/MRA"
        },
        {
            "id": "1690065138_recruiting_pre_scre",
            "title": "Miscellaneous"
        },
        {
            "id": "new_group32939",
            "title": "Test"
        }
    ]
}
OCCUPATION_MAP = {'Therapist': 3, 'Nurse': 105, 'Sales Rep': 156, 'VOB': 0, 'MRA': 1, 'MRA, LVN': 2, 'VOB/MRA': 4, 'EA': 6, 'Event Planner': 7, 'BD/Admissions': 8, 'Jr. Recruiter': 9, 'Recruiter': 10, 'RADT/CADC/Tech': 11, 'Med Office Admin': 12, 'Podcast Producer': 13, 'Front Desk Receptionist': 14, 'Surgical Tech': 15, 'Aesthetic Nurse': 16, 'EMT': 17, 'Office Clerk': 18, 'LVN': 19, 'Call Center Rep': 101, 'Tech': 102,
                  'MRA/Biller': 103, 'Tech/Tech Manager': 104, 'Group Facilitator': 106, 'Medical Records Assistant': 107, 'Specimen Processor': 108, 'Call Center Rep (Magnified Health)': 109, 'Medical Technologist': 110, 'Admin': 151, '(LA) Group Facilitator': 152, 'Recruiter? Unknown': 153, 'Therapist? Unknown': 154, 'Lab Scientist': 155, 'Program and Clinical Director': 157, 'Fulfillment Manager': 158, 'Clinical Director': 159, 'Program Director': 160}


def get_Monday_group(group: str) -> str:
    title_to_id_map = {group["title"]: group["id"]
                       for group in GROUP_ID_MAP["groups"]}
    return title_to_id_map.get(group, DEFAULT_GROUP)


async def createMondayItem(data: candidateData):
    """
    Principal function to upload info to Monday DB,
    -> returns ID of newly created item (if created) 
    """

    # Read sheet positional settings data
    f = open(SETTINGS_PATH)
    setting_data = json.load(f)

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey, "API-version": "2023-04"}

    # Remove non-digits from phone #
    phone = ""
    if data.phone != None and data.phone != "None":
        phone = ''.join(c for c in data.phone if c.isdigit())

    # Assign Column values if found
    column_values = {
        # Occupation
        "label": f"{OCCUPATION_MAP.get(setting_data['occupation'], 0)}",
        "status4": data.source,  # Source
        # "location": data.location,  # Location #TODO Create a real location coordinate generator
        "text8": data.location,  # Location
        "phone": phone,
        "email": {"email": data.email, "text": data.email},  # Email
        "text": data.license_cert  # License/Certification (null OK)
    }

    j = json.dumps(column_values)
    j = j.replace('"', '\\\"')

    GROUP_ID = get_Monday_group(setting_data['group'])

    # Generate mutation
    createItemMutation = f'''mutation {{
        create_item (
            board_id: {BOARD_ID} 
            group_id: "{GROUP_ID}" 
            item_name: "{data.name}" 
            column_values: "{j}") {{id}}
            }}'''

    d = {"query": createItemMutation}

    # Send mutation (async?)
    response = requests.post(url=apiUrl, json=d, headers=headers)

    # Handle response
    if response.status_code == 200:
        response_data = response.json()
        new_id = response_data['data']['create_item']['id']
        logger.info(
            f"{data.name} - Successfully Added Candidate to Monday at: {new_id}")
        return new_id
    else:
        logger.info(f"{data.name} - Failed to upload  to Monday")
        return None


async def updateMondayItem(data: candidateData):
    """
    Updates item of monday item based on a pre-determined item ID
    """

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey, "API-version": "2023-04"}

    # Remove non-digits from phone #
    phone = ""
    if data.phone != None and data.phone != "None":
        phone = ''.join(c for c in data.phone if c.isdigit())

    # Assign Column values if found
    column_values = {
        # "location": data.location,  # Location #TODO Create a real location coordinate generator
        "phone": phone,
        "email": {"email": data.email, "text": data.email},  # Email
        # "text": data.license_cert  # License/Certification (null OK) TODO
    }

    # Format column_values
    j = json.dumps(column_values)
    j = j.replace('"', '\\\"')

    # Generate mutation
    createItemMutation = f'''mutation {{
        change_multiple_column_values (
            item_id: {data.monday_id}
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
            f"{data.name} - Updated phone/email information at: {new_id}")
    else:
        logger.info(f"{data.name} - Failed to update Monday values")

    return


async def uploadCandidateResume(data: candidateData):
    # Get newest file
    list_of_files = glob.glob(DOWNLOAD_PATH)  #  + "/*" for Mac 
    f = max(list_of_files, key=os.path.getctime)

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    headers = {
        "Authorization": apiKey,
        "API-version": "2023-04"
    }
    url = "https://api.monday.com/v2/file"

    # Generate Mutation
    q = f"""
            mutation add_file($file: File!) {{
                add_file_to_column (
                    item_id: {data.monday_id},
                    column_id: files,
                    file: $file
                        ){{
                    id
                }}
            }}
        """

    file_type = "application/pdf"
    if ".pdf" not in f:
        # Should revise this but for now seem to only be dealing with pdf resumes
        file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    files = {
        'query': (None, q, f'{file_type}'),
        'variables[file]': (f, open(f, 'rb'), 'multipart/form-data', {'Expires': '0'})
    }

    # Send Request
    response = requests.post(url=url, files=files, headers=headers)

    # Handle response
    if response.status_code == 200:
        # response_data = response.json()
        logger.info(f"{data.name} - Successfully uploaded Resume")
    else:
        logger.info(f"{data.name} - Failed to upload Resume")

    return


async def createQuestionDocument(data: candidateData):
    """
    Creates a 'Monday Doc' in the candidate's 'Notes' field
    """

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    headers = {
        "Authorization": apiKey,
        "API-version": "2023-04"
    }
    url = "https://api.monday.com/v2"

    # Generate Mutation
    q = f"""
            mutation 
                {{ 
                    create_doc (
                        location: {{
                            board : {{
                                item_id : {data.monday_id},
                                column_id: monday_doc6,
                            }}
                        }}
                    )
                    {{
                        id
                    }}
                }}
        """

    # Send Request
    response = requests.post(url=url, headers=headers, json={'query': q})

    # Handle response
    if response.status_code == 200:
        response_data = response.json()
        data.notes_id = response_data['data']['create_doc']['id']
        logger.info(f"{data.name} - Updated notes_id local field")
        logger.info(f"{data.name} - Successfully created Notes document")

    else:
        logger.info(f"{data.name} - Failed to create Notes document")

    return


async def updateQuestionDocument(data: candidateData):
    """
    Updates the 'Monday Doc' in the candidate's 'Notes' field
    This function depends on the occupation of the candidate and will default to a general (Therapist) questionairre
    """

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    headers = {
        "Authorization": apiKey,
        "API-version": "2023-04"
    }
    url = "https://api.monday.com/v2"

    # JSON
    column_values = {
        "alignment": "left",
        "direction": "ltr",
        "deltaFormat": [
        ]
    }

    # Pick Questionairre format
    delta_format = GetQuestionSheet(data)  # TODO

    # Format for Monday request
    column_values["deltaFormat"] = delta_format
    j = json.dumps(column_values)
    j = j.replace('"', '\\\"')

    # Generate Mutation
    q = f"""
            mutation 
                {{ 
                    create_doc_block (
                        type: normal_text
                        doc_id: {data.notes_id}
                        content : "{j}"
                    )
                    {{
                        id
                    }}
                }}
        """

    # Send request
    response = requests.post(url=url, headers=headers, json={'query': q})

    # Handle response
    if response.status_code == 200:
        response_data = response.json()
        logger.info(
            f"{data.name} - Successfully updated Notes document with questionnaire info")
    else:
        logger.info(
            f"{data.name} - Failed to update Notes document with questionnaire info")

    return


def GetQuestionSheet(data: candidateData) -> dict:
    """
    Helper function to return the correct information to put in the candidate's 'Notes' questionairre
    """
    # Read sheet positional settings data
    f = open(SETTINGS_PATH)
    setting_data = json.load(f)

    if setting_data['occupation'] is "Nurse":
        lines = [
            f"Date: {data.date}",
            f"Location: {data.location}",
            "Willingness to commute to?:",
            "Yrs Exp w/ Treatment?:",
            "If so, where?:",
            "Yrs Exp w/ Kipu?:",
            "If not, tech savvy?:",
            "Doctor’s Orders?:",
            "COWS/CIWA?:",
            "FT/PT/Per Diem?:",
            "When Start?:",
            "Desired Hours?:",
            "Desired Wage?:",
            "Availability?:",
            "Open to nights?:",
            "Med Destruction?:",
            "Licenses and certs?:",
            "Verified?:",
            "Active CPR/FA?:",
            "Other Notes?:"
        ]
    elif setting_data['occupation'] is "Front Desk Receptionist":
        lines = [
            f"Date Applied: {data.date}",
            "Date Interviewed:",
            f"Location: {data.date}",
            "How far are you willing to commute?:",
            "Medical Office Experience?:",
            "If so, where?:",
            "Specialty?:",
            "EMR Experience?:",
            "FT/PT?:",
            "Desired Wage?:",
            "When can you start?:",
            "Additional Certifications:",
            "General Notes:"
        ]
    else:
        # Defaults to Therapist Questionairre
        lines = [
            f"Certification Type and  #: {data.license_cert}, {data.license_expiration}",
            f"Date: {data.date}",
            f"Location: {data.location}",
            "How far are you willing to commute?:",
            "Treatment Experience?:",
            "If so, where?:",
            "Kipu Experience?:",
            "If not, tech savvy?:",
            "BPS/Treatment Plans/ASAM Criteria/Utilization Review?:",
            "FT/PT/Groups?:",
            "What kind of groups?:",
            "Telehealth exp?:",
            "Desired Wage?:",
            "When can you start?:",
            "CPR/FA?:",
            "Additional Certifications:",
            "Hours Towards Licensure:",
            "General Notes:"
        ]

    delta_format = [{"insert": line + '\\n\\n'} for line in lines]

    return delta_format

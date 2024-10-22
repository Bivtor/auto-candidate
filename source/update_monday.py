import requests
import os
import json
import re
import glob
from dotenv import load_dotenv
from paths import ENV_PATH, SETTINGS_PATH, DOWNLOAD_PATH, RECEIPT_PATH
from auto_candidate import candidateData, logger, Data
from location_detection import compute_location_area
import time

load_dotenv(dotenv_path=ENV_PATH)

BOARD_ID = 4846750007
# Miscellaneous -> Switched to random text -> Fail > mis input / mis text


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
        "label": f"{setting_data['occupation']['id']}",
        "status4": data.source,  # Source
        # "location": data.location,  # Location #TODO Create a real location coordinate generator
        "text8": data.location,  # Location
        "phone": phone,
        "email": {"email": data.email, "text": data.email},  # Email
        "text": data.license_cert  # License/Certification (null OK)
    }

    j = json.dumps(column_values)
    j = j.replace('"', '\\\"')

    GROUP_ID = setting_data['group']['id']

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
        logger.info(f"{data.name} - Failed to upload to Monday")
        logger.info(response.json())
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
    list_of_files = glob.glob(DOWNLOAD_PATH)
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
                    column_id: "files",
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

    # logger.info(f"query: {files}")

    # Send Request
    response = requests.post(url=url, files=files, headers=headers)

    # Handle response
    if response.status_code == 200:
        response_data = response.json()
        logger.info(f"{data.name} - Successfully uploaded Resume")
        logger.info(f"Response: {response_data}")
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

    if setting_data['occupation'] == "Nurse":
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
    elif setting_data['occupation'] == "Front Desk Receptionist":
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


def updateCandidateTextStatus(candidate_id: int, log_name: str, new_status: str, ):
    """
    Updates the text status of 'candidate_id' to 'new_status'
    Text status field has id='status_1'
    """

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    headers = {
        "Authorization": apiKey,
        "API-version": "2023-04"
    }
    url = "https://api.monday.com/v2"

    # Generate Query
    q = f"""
        mutation
        {{
            change_simple_column_value (
                item_id: {candidate_id},
                board_id: {BOARD_ID},
                column_id : "status_1", 
                value: "{new_status}"
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
        logger.info(
            f"{log_name} - Successfully updated Monday Status to {new_status}")
    else:
        logger.info(
            f"{log_name} - Failed to Update Monday Status to {new_status}")
    return


def updateCandidateLaArea(monday_id: str, LA_area: str, name: str):
    """
    Updates the 'LA Area' field of 'monday_id' 
    """

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    headers = {
        "Authorization": apiKey,
        "API-version": "2023-04"
    }

    url = "https://api.monday.com/v2"

    # Generate Query
    q = f"""
        mutation
        {{
            change_simple_column_value (
                item_id: {monday_id},
                board_id: {BOARD_ID},
                column_id : "status_14", 
                value: "{LA_area}",
                create_labels_if_missing:true
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
        logger.info(
            f"{name} - Successfully Updated LA Area Status to {LA_area}")
    else:
        logger.info(
            f"{name} - Failed to Update LA Area Status to {LA_area}")

    return


def updateLA_Area(loc: str, monday_id: str, name: str):
    """
    Recieved Location text and monday ID
    Computes LA_Area field and updates monday

    name for logging only
    """

    # Skip update if location is empty
    if len(loc) == 0 or loc == "" or len(loc.strip()) == 0:
        logger.info(f"{name} - Location Empty, Did Not Update LA_Area Field")
        return

    # Get LA_Area
    LA_area = compute_location_area(loc)

    # Update Location on Monday
    # Name is for logging, successful update logged inside of this function
    updateCandidateLaArea(
        LA_area=LA_area,
        monday_id=monday_id,
        name=name)


def getGroupMessageInfo(input_data: Data) -> dict:
    """
    Function for Text/Mail Program that returns a dictionary with Candidate: Name, ID, & ShouldText
    """

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    headers = {
        "Authorization": apiKey,
        "API-version": "2023-04"
    }
    url = "https://api.monday.com/v2"

    # Generate Query
    # TODO Add code that defaults to fail if we cannot find the proper group id
    q = f"""
    {{
        boards(ids: {BOARD_ID}) 
        {{
            groups(ids: "{input_data.group.id}")
            {{
                items 
                {{
                    id
                    name
                    column_values (ids: ["status_1", "phone", "email"]) 
                    {{
                        text
                        id
                    }}
                }}
            }} 
        }}
    }}
        """

    # Send request
    response = requests.post(url=url, headers=headers, json={'query': q})

    # Handle response
    if response.status_code == 200:
        response_data = response.json()

        # Log
        logger.info(
            f"{input_data.group.title} Text Order - Successfully got Info from Monday for Message Program")

        # Append to receipt file
        append_text_to_file(
            RECEIPT_PATH, f"{input_data.group.title} Text Order - Successfully got Info from Monday for Message Program\n\n"
        )

        return response_data
    else:
        # Log
        logger.info(
            f"{input_data.group.title} Text Order - Failed to get Info from Monday for Message Program")

        # Append to receipt file
        append_text_to_file(
            RECEIPT_PATH, f"{input_data.group.title} Text Order - Failed to get Info from Monday for Message Program\n"
        )
        return {}

# Old Functions used for One-Time updating of entire Monday Groups


def getAllCandidatesInGroup(group: str):
    """
    Helper function for one-time update all location based on where they are in LA Function
    """

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    headers = {
        "Authorization": apiKey,
        "API-version": "2023-04"
    }

    url = "https://api.monday.com/v2"

    # Generate Query
    q = f"""
        {{
            boards(ids: 4846750007) {{
                groups(ids: "{group}") {{
                    items {{
                        id
                        name
                        column_values(ids: ["text8"]) {{
                            text
                        }}
                    }}
                }}
            }}
        }}
        """

    # Send request
    response = requests.post(url=url, headers=headers, json={'query': q})

    # Handle response
    if response.status_code == 200:
        # logger.info(
        #     f"{candidate_profile.name} - Successfully Updated LA Area Status to {candidate_profile.LA_area}")
        pass
    else:
        pass
        # logger.info(
        #     f"{candidate_profile.name} - Failed to Update LA Area Status to {candidate_profile.LA_area}")

    response_data = response.json()
    data = response_data['data']['boards'][0]['groups'][0]['items']
    return data


def updateOldMondayCandidates():
    """
    One-off function to update old candidates to put them somewhere in LA based on location column 
    """

    # Get response (list of people in the group)
    candidate_list = getAllCandidatesInGroup("1690064031_recruiting_pre_scre")

    # Iterate through list and update value of candidate ID to
    for candidate in candidate_list:
        # Get their location
        loc = candidate['column_values'][0]['text']

        # Skip if empty
        if len(loc) == 0 or loc == "" or len(loc.strip()) == 0:
            continue

        # Compute their LA Area Location
        LA_area = compute_location_area(loc)

        # Update Location on Monday
        updateCandidateLaArea(
            LA_area=LA_area,
            monday_id=candidate['id'],
            name=candidate['name'])

        # Wait to not API too fast
        time.sleep(.4)


def append_text_to_file(file_path, text):
    """
    Appends text to receipt file
    """
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(text)
    except Exception as e:
        print(f"An error occurred while appending to '{file_path}': {str(e)}")

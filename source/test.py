import requests
import glob
import asyncio
import os
import json
from dotenv import load_dotenv
from paths import ENV_PATH, SETTINGS_PATH, DOWNLOAD_PATH
from pydantic import BaseModel


class candidateData(BaseModel):
    hasResume: bool | None
    location: str | None
    name: str | None
    phone: str | None
    email: str | None
    date: str | None
    pagelink: str | None
    source: str | None
    license_cert: str | None
    license_expiration: str | None
    resume_download_link: str | None
    candidate_folder_id: str | None
    candidate_resume_id: str | None
    candidate_document_id: str | None
    title: str | None


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


def get_Monday_group(group: str) -> str:
    title_to_id_map = {group["title"]: group["id"]
                       for group in GROUP_ID_MAP["groups"]}
    return title_to_id_map.get(group, "new_group32939")

# Read sheet positional settings data


def test():
    f = open(SETTINGS_PATH)
    setting_data = json.load(f)

    apiKey = os.environ['MONDAY_API_KEY']
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey,
               "API-version": "2023-04",
               'Content-Type': 'application/json', }
    GROUP_ID = get_Monday_group(setting_data['group'])

    items = {
        "location": "Los Angeles",
        "item2": 2013902139,
        "email": {"email": "victorinaldi@ucla.edu", "text": ""},  # Email

    }

    j = json.dumps(items)
    j = j.replace('"', '\\"')

    createItemMutation = f"mutation {{ create_item (board_id: {BOARD_ID} column_values : \" {j} \") {{id}}}}"

    # print(createItemMutation)

    column_values = {
        "label": "0",
        "status4": "Indeed",
        "text8": "None",
        "phone": "",
        "email": {
            "email": "crystalwilliams734_cp2@indeedemail.com",
            "text": ""
        },
        "text": ""
    }

    mutation = '''
    mutation {
    create_item(
        board_id: "4846750007"
        group_id: "new_group32939"
        item_name: "Crystal Williams"
        column_values: "%s"
    ) {
        id
    }
    }
    ''' % json.dumps(column_values)

    # print(mutation)
# Assign values
    column_values = {
        # Occupation
        "label": "0",
        "status4": "2",  # Source
        # "location": data.location,  # Location #TODO Create a real location coordinate generator
        "text8": "Therapist",  # Location Text
        "phone": "9805722784",
        "email": {"email": "data.email", "text": ""},  # Email
        "text": "THis ithe cert"  # License/Certification (null OK)
    }

    j = json.dumps(column_values)
    j = j.replace('"', '\\\"')
    # print(j)

    createItemMutation = f'mutation {{create_item (board_id: {BOARD_ID}, group_id: "{GROUP_ID}", item_name: "VICTOR", column_values:" {j} " ) {{id}}}}'

    r = {"query": createItemMutation}

    print("\n", r, "\n")

    response = requests.post(
        url=apiUrl, json=r, headers=headers, )

    if response.status_code == 200:
        data = response.json()
        print("\n", data)
    else:
        print('Request failed with status code:', response.status_code)
        print('Response:', response.text)


async def updateMondayItem():
    """
    Updates item of monday item based on a pre-determined item ID
    """

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey, "API-version": "2023-04"}

    # Remove non-digits from phone #

    # if data.phone != None and data.phone != "None":
    #     phone = ''.join(c for c in data.phone if c.isdigit())

    phone = "8057227847"
    email = "kingvictork10@gmailll.com"

    # Assign Column values if found
    column_values = {
        # "location": data.location,  # Location #TODO Create a real location coordinate generator
        "phone": phone,
        "email": {"email": email, "text": email},  # Email
        # "text": data.license_cert  # License/Certification (null OK)
    }

    j = json.dumps(column_values)
    j = j.replace('"', '\\\"')

    # Generate mutation
    createItemMutation = f'''mutation {{
        change_multiple_column_values (
            item_id: 4945253833 
            board_id: 4846750007
            column_values : "{j}") {{id}}
            }}
            '''

    d = {"query": createItemMutation}

    # Send mutation (async?)
    response = requests.post(url=apiUrl, json=d, headers=headers)

    # Handle response
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        # new_id = response_data['data']['create_item']['id']
        # print(new_id)
        # return new_id
    else:
        print("Fail")
        return None


async def uploadCandidateResume():
    # Get newest file 'path'
    list_of_files = glob.glob(DOWNLOAD_PATH + "/*")
    f = max(list_of_files, key=os.path.getctime)

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    headers = {"Authorization": apiKey,
               "API-version": "2023-04"
               }

    # Generate Mutation
    url = "https://api.monday.com/v2/file"

    q = f"""
            mutation add_file($file: File!) {{
                add_file_to_column (
                    item_id: 4976357521,
                    column_id: files,
                    file: $file
                        ){{
                    id
                }}
            }}
        """

    files = {
        'query': (None, q, 'application/pdf'),
        'variables[file]': (f, open(f, 'rb'), 'multipart/form-data', {'Expires': '0'})
    }

    response = requests.post(url=url, files=files, headers=headers)

    # Handle response
    print(response.json())

    return


async def createQuestionDocument():
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
                                item_id : 4976409772,
                                column_id: monday_doc6,
                            }}
                        }},
                    )
                    {{
                        id
                    }}
                }}
        """

    response = requests.post(url=url, headers=headers, json={'query': q})

    # Handle response
    response_data = response.json()
    print(response_data)

    return


async def updateQuestionDocument():  # data: candidateData
    """
    Updates the 'Monday Doc' in the candidate's 'Notes' field

    This function depends on the occupation of the candidate and will default to some certain structure
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
    delta_format = GetQuestionSheet()  # data # TODO

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
                        doc_id: 7218454
                        content : "{j}"
                    )
                    {{
                        id
                    }}
                }}
        """

    print(q)
    print()
    response = requests.post(url=url, headers=headers, json={'query': q})

    # Handle response
    response_data = response.json()
    print(response_data)

    return


def GetQuestionSheet() -> dict:  # data
    # if data.occupation is "Therapist":
    lines = [
        "Certification Type and  #:",
        "Date:",
        "Location:",
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


# # test()
loop = asyncio.get_event_loop()
loop.run_until_complete(updateQuestionDocument())
# GetQuestionSheet()

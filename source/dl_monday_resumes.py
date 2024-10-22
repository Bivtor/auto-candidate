import requests
import os
from dotenv import load_dotenv
from paths import ENV_PATH, OPEN_CMD_LINK
import time

# Test Query for API playground
# {
#   boards(ids: 4846750007) {
#     groups(ids: "new_group77888") {
#       items_page(limit:500) {
#         items {
#           name
#           column_values(ids: ["files"]) {
#             text
#           }
#         }
#       }
#     }
#   }
# }

# Get Groups Query for API Playground 
# {
#   boards(ids: 4846750007) {
#     groups {
#       title
#       id
#     }
#   }
# }

load_dotenv(dotenv_path=ENV_PATH)

BOARD_ID = 4846750007
MONDAY_API_KEY="eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI5MTI3Nzc4OCwiYWFpIjoxMSwidWlkIjo1MDcwNTgxMSwiaWFkIjoiMjAyMy0xMC0yNFQwMDoyNzoyOS40NDdaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTQzMjg5NDQsInJnbiI6InVzZTEifQ.yu1xSIeWUNYmKOCyW40EjkxdkUlkE45VAC-vZFtTSXg"

# Miscellaneous -> Switched to random text -> Fail > mis input / mis text

# Used for One-Time getting of entire monday group
def get_all_resume_links(group: str):
    """
    Function that gets the link to the resume that monday holds for each candidate in the provided group
    """

    # Monday Code
    apiKey = MONDAY_API_KEY


    headers = {
        "Authorization": apiKey,
        "API-version": "2023-04"
    }

    url = "https://api.monday.com/v2"
    

    q = f"""
        {{
        boards(ids: 4846750007) {{
            groups(ids: "{group}") {{
                items_page(limit: 100) {{
                    items {{
                    name
                    column_values(ids: ["files"]) {{
                        text
                    }}
                    }}
                    cursor
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
        data = response_data['data']['boards'][0]['groups'][0]['items_page']
        return data
    else:
        pass

def get_next_resume_links(cursor: str):
    """
    NEXT RESUMES
    """

    # Monday Code
    apiKey = MONDAY_API_KEY


    headers = {
        "Authorization": apiKey,
        "API-version": "2023-04"
    }

    url = "https://api.monday.com/v2"
    

    q = f"""
        {{
            next_items_page(limit: 100, cursor: \"{cursor}\") {{
            cursor
                items {{
                name
                column_values(ids: ["files"]) {{
                    text
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
        # print(q)
        # print(response_data)
        data = response_data['data']['next_items_page']
        return data
    else:
        pass

def open_link(link: str):
    cmd = OPEN_CMD_LINK.format(link)
    if os.system(cmd) == 0:
        print("Success")
    else:
        print("Failure")



group = "new_group13921" # Set Target Group
r = get_all_resume_links(group)
r_items = r['items']
r_cursor = r['cursor']

for i, person in enumerate(r_items):
    name = person['name']
    print("Name: " + name)
    p = person['column_values'][0]['text']
    if (len(p)) > 0:
        print("Found Resume")
        open_link(p)
    else: 
        print("No Resume")
    print(f"person #{i+1}")
    time.sleep(0.1)
if r_cursor != None:
    print("Cursor: " + r_cursor)
else: 
    print("No cursor")
req_n = 1

# Do rest of items
while (r_cursor != None):
    print("Request # ", req_n)
    req_n+=1
    next_results = get_next_resume_links(r_cursor)
    r_cursor = next_results['cursor']
    r_results = next_results['items']
    
    # Perform operations
    for i, person in enumerate(r_results):
        name = person['name']
        print("Name: " + name)
        p = person['column_values'][0]['text']
        if (len(p)) > 0:
            print("Found Resume")
            open_link(p)
        else: 
            print("No Resume")
        print(f"person #{i+1}")
        time.sleep(0.1)
    


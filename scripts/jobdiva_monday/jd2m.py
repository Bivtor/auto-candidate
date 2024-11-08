import aspose.words as aw
import json
import glob
import requests
from dotenv import load_dotenv
import csv
import os
import time
from location_detection import compute_location_area
from occupation_detection import getOccupationWrapper
from base import *
from typing import Optional

load_dotenv(dotenv_path=ENV_PATH)


def load_candidate_data_from_csv(row: dict) -> CandidateData:
    """
    Step 2: Load candidate data from the CSV row into the CandidateData object.
    """
    candidate = CandidateData(
        name=f"{row['FIRSTNAME']} {row['LASTNAME']}",
        email=row['EMAIL'],
        location=f"{row['ADDRESS1']} {row['ZIPCODE']} {row['CITY']} {row['STATE']}",
        phone=row['CELLPHONE'],
        jobdiva_id=row['ID']
    )
    return candidate


def check_monday_for_candidate(name: str) -> bool:
    """
    Step 3: Check if the candidate already exists on Monday.com.

    Placeholder for Monday.com API call:
    If the candidate exists, return True; otherwise, return False.
    """
    # TODO: Implement Monday.com API call to check for candidate existence
    logger.info(f"{name} - Checking if already exists on Monday")

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
        {{
        items_page_by_column_values (limit: 50, board_id: {BOARD_ID}, columns: [{{column_id: "name", column_values: [\"{name}\"]}}]) {{
            items {{
                id
                name
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
        # Log
        # logger.info(f"{name} - Successfully got info from monday")

        if (len(response_list) > 0):
            logger.info(
                f"-------> {name} already exists on Monday.com, skipping.")
            return True
        else:
            logger.info(
                f"{name} - Candidate not found on Monday.com, continuing process.")
            return False
    else:
        # Handle get info fail
        logger.info(
            f"{name} Failed to get Info from Monday, continuing process.")
        return False


def search_resume_by_global_id(candidate_id: str) -> Optional[str]:
    """
    Step 4: Search resume.csv for a globalID associated with the candidateID.
    """

    def convert_rtf_to_pdf(rtf_file: str) -> str:
        """
        Converts an RTF file to a PDF.
        This is a placeholder for the actual conversion logic.
        Returns the new PDF file name.
        """
        logger.info(f'Found RTF file instead of PDF, converting file to PDF')
        doc = aw.Document(rtf_file)

        pdf_file = rtf_file.replace('.rtf', '.pdf')

        logger.info(f"Converting {rtf_file} to {pdf_file} ")

        doc.save(pdf_file)

        return pdf_file

    def chooseReturnFile(files: list) -> Optional[str]:
        """
        Helper Function:
        Given a list of file names, this function returns a suitable file name.

        If a file with a .pdf extension exists, return that file.
        If not, and a file with an .rtf extension exists, convert it to a .pdf and return the new file name.
        """
        # Check for a PDF file
        for file in files:
            if file.lower().endswith('.pdf'):
                return file

        # Check for an RTF file and convert it to a PDF
        for file in files:
            if file.lower().endswith('.rtf'):
                converted_file = convert_rtf_to_pdf(file)
                return converted_file

        # Return None if no suitable file is found
        return None

    try:
        # Search in resume.csv
        with open(RESUME_CSV_PATH, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['CANDIDATEID'] == candidate_id:
                    # Extract the GLOBAL_ID from the matching row
                    global_id = row['GLOBAL_ID']

                    logger.info(
                        f'Found Resume Identification number: {global_id}')
                    # Find matching files
                    matching_files = glob.glob(os.path.join(
                        RESUME_FOLDER_PATH, f"{global_id}*"))

                    # Log
                    if len(matching_files) > 0:
                        logger.info(f'Found Resume file(s): {matching_files}')
                    else:
                        logger.info(f'Did not find resume files')
                        return None

                    # Return the file that we want from the list
                    chosen_file = chooseReturnFile(matching_files)
                    logger.info(f'Found file: {chosen_file}')

                    return chosen_file if chosen_file else None
        return None

    except FileNotFoundError:
        print(f"{RESUME_CSV_PATH} not found.")
        return None


def search_notes_by_jobdiva_id(jobdiva_id: str) -> Optional[str]:
    """
    Search candidatenote.csv for all rows matching the jobdiva_id and return
    a formatted string with Recruiter, Date, and Note for each matching entry.
    """
    try:
        # Load recruiters data into a dictionary for quick lookup by RECRUITERID
        recruiter_dict = {}
        with open(RECRUITERS_CSV_PATH, mode='r') as recruiters_file:
            recruiter_reader = csv.DictReader(recruiters_file)
            for recruiter in recruiter_reader:
                recruiter_dict[recruiter['ID']
                               ] = f"{recruiter['FIRSTNAME']} {recruiter['LASTNAME']}"

        # Prepare a list to hold all matching notes
        notes_list: list[str] = []

        # Search the candidatenote.csv for notes corresponding to the jobdiva_id
        with open(CANDIDATE_NOTES_CSV_PATH, mode='r') as notes_file:
            notes_reader = csv.DictReader(notes_file)
            for row in notes_reader:
                if row['CANDIDATEID'] == jobdiva_id:
                    # Get recruiter name using RECRUITERID from the current row
                    recruiter_name = recruiter_dict.get(
                        row['RECRUITERID'], "Unknown Recruiter")
                    date_created = row['DATECREATED']
                    note = row['NOTE']

                    # Append formatted note details to the list
                    notes_list.append(
                        f"Recruiter: {recruiter_name}\nDate: {date_created}\nNote: {note}\n")

        # If there are any matching notes, return them as a single formatted string
        if notes_list:
            # logger.info("\n\n".join(notes_list))
            # Log
            logger.info(f"Found candidate notes")
            return "\n\n".join(notes_list)
        else:
            # Return None if no matching jobdiva_id is found
            logger.info(f"Did not find any candidate notes")
            return None

    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return None


def createMondayItem(data: CandidateData):
    """
    Principal function to upload info to Monday DB,
    -> returns ID of newly created item (if created) 
    """

    # Monday Code
    apiKey = os.environ['MONDAY_API_KEY']
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": apiKey, "API-version": "2023-04"}

    # Assign Column values if found

    # Column Values
    column_values = {
        "occupation__1": str(data.occupation_id),  # Occupation
        "status4": data.source,  # Source
        "text8": data.location,  # city, state
        "phone": data.phone,  # Phone
        "email": {"email": data.email, "text": data.email},  # Email
        "text": data.license_cert,  # License/Certification (null OK)
        # Location coords
        "location__1": f"{data.GPS_COORD['lat']} {data.GPS_COORD['long']} {data.location}",
        "status_14": data.LA_area,  # LA Area field
    }

    # Values when location is not found
    column_values_no_locations = {
        "label": str(data.occupation_id),  # Occupation
        "status4": data.source,  # Source
        "phone": data.phone,  # Phone
        "email": {"email": data.email, "text": data.email},  # Email
        "text": data.license_cert,  # License/Certification (null OK)
        # Location coords
        "status_14": data.LA_area,  # LA Area field
    }

    # Do not upload area blanks if there is no area
    if (
        data.LA_area == " "
        or data.LA_area is None
        or data.GPS_COORD['lat'] is None
        or data.GPS_COORD['long'] is None
        or not isinstance(data.GPS_COORD['lat'], (int, float))
        or not isinstance(data.GPS_COORD['long'], (int, float))
    ):
        # Your code here
        logger.info(
            f'{data.name} - Fell into second candidate upload format without location')
        column_values = column_values_no_locations

    j = json.dumps(column_values)
    j = j.replace('"', '\\\"')

    # Generate mutation
    createItemMutation = f'''mutation {{
        create_item (
            board_id: {BOARD_ID} 
            group_id: "{GROUP_ID}" 
            item_name: "{data.name}" 
            column_values: "{j}") {{id}}
            }}'''

    # Create query
    q = {"query": createItemMutation}

    # Send query
    response = requests.post(url=apiUrl, json=q, headers=headers)

    # Handle response
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        new_id = response_data['data']['create_item']['id']
        data.monday_id = new_id
        logger.info(
            f"{data.name} - Successfully Added Candidate to Monday at: {new_id}")
        return new_id
    else:
        logger.error(f"{data.name} - Failed to upload to Monday")
        logger.info(response.json())
        return


def updateCandidateNotesFromJobDiva(data: CandidateData):
    """
    Updates the candidate's notes in Monday.com.
    This function sends a mutation to add an update to the specified item based on the candidate data.
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
            mutation {{
                create_update (
                    item_id: {data.monday_id},
                    body: "{data.jobdiva_notes}"
                ) {{
                    id
                }}
            }}
        """

    # Send request
    response = requests.post(url=url, headers=headers, json={'query': q})

    # Handle response
    if response.status_code == 200:
        # response_data = response.json()
        logger.info(
            f"{data.name} - Successfully updated candidate notes")
    else:
        logger.info(
            f"{data.name} - Failed to update candidate notes")

    return


def uploadCandidateResume(data: CandidateData, f: str):

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

    files = {
        'query': (None, q, f'{file_type}'),
        'variables[file]': (f, open(f, 'rb'), 'multipart/form-data', {'Expires': '0'})
    }

    # Send Request
    response = requests.post(url=url, files=files, headers=headers)

    # Handle response
    if response.status_code == 200:
        response_data = response.json()
        logger.info(f"{data.name} - Successfully uploaded Resume")
        # logger.info(f"Response: {response_data}")
    else:
        logger.info(f"{data.name} - Failed to upload Resume")

    return


def updateLA_Area(data: CandidateData):
    """
    Updates CandidateData object LA_area and 
    """

    # Skip update if location is empty
    if len(data.location) == 0 or data.location == "" or len(data.location.strip()) == 0:
        logger.info(
            f"{data.name} - Location Empty, Set LA Area to unknown")
        return

    # Get LA_Area
    data.LA_area = compute_location_area(data)
    logger.info(f"{data.name} - -> Set LA Area to {data.LA_area}")

    # Log
    logger.info(f"{data.name} - -> Detected LA Area")

    return


def determineOccupation():
    pass


def run(start_idx: int, end_idx: int):
    """
    Driver code for running program on resumes

    Open candidate.csv and step through denoted range of candidates (0 - 100)
    Create a passed down candidateData object
    For each row, complete steps 1-10:

    - Step 1:
        Pull info from candidate.csv and update candidateData object:
            Name (FIRSTNAME, " ", LASTNAME)
            Email (EMAIL)
            Address (ADDRESS1, " ", ZIPCODE, " ", CITY, " ", STATE )
            Phone Number (CELLPHONE)
            jobdiva_id (ID)

    - Step 2:
        Ask Monday.com if this candidate name already exists:
            if it does -> exit
            if it does not -> proceed

    - Step 3:
        Search resume.csv for global_ID in row matching jobdiva_id
        Search folder for resume file with matching global_ID

    - Step 4:
        Search candidatenotes.csv for row matching jobdiva_id
        Search recruiter.csv to find the matching recruiter_id and denote the person who made the note

    - Step 5:
        Decide Occupation based on text from resume and from notes

    - Step 9: 
        Update LA area field
        Update location field

    - Step 6:
        Upload candidate data from candidateData object to Monday.com
        monday_id is returned, rest of functions are updating the candidate associated with this monday_id

    - Step 7:
        Aggregate and format JobDiva notes and add a monday 'update' with the notes

    - Step 8:
        Upload resume to monday

    Notes:
        - Ignoring dates for now
        - Group labels are impossible to determine through the given data, will have to do by hand later
        - Job labels are mostly listed for candidates we already have, and are mostly missing other than that,
            will also have to complete by hand after uploading to monday

    TODO:
        - Choose occupation
            - Options:
                1 Train a classifier on 
        - Add license
    """

    # try:
    logger.info(
        f'------------------ STARTING CANDIDATE ADD: {start_idx} - {end_idx} ------------------')
    with open(CANDIDATE_CSV_PATH, mode='r') as file:
        reader = csv.DictReader(file)
        for idx, row in enumerate(reader):
            # Process correct rows
            if idx < start_idx:  # Skip rows before the start index
                continue
            if idx >= end_idx:  # Stop processing once end index is reached
                break

            logger.info(
                f'---------------------------------------------#{idx}---------------------------------------------')

            # Step 1: Load candidate data
            candidate_data = load_candidate_data_from_csv(row)
            logger.info(
                f'{candidate_data.name} - JobDiva Candidate ID - {candidate_data.jobdiva_id}')

            # Check for malformed data and skip
            if candidate_data.name.lower() == "style":
                logger.info(
                    f'{candidate_data.name} - Detected Malformed entry, skipping')
                continue

            # Step 2: Check if candidate exists on Monday.com
            if check_monday_for_candidate(candidate_data.name):
                continue

            # Step 3: Search resume
            resume_path = search_resume_by_global_id(
                candidate_data.jobdiva_id)
            candidate_data.hasResume = resume_path is not None
            candidate_data.resume_file = resume_path

            # Step 4: Search for candidate notes
            notes = search_notes_by_jobdiva_id(candidate_data.jobdiva_id)
            candidate_data.hasNotes = notes is not None
            candidate_data.jobdiva_notes = notes

            # Step 5: decide occupation based on resume text
            occupation_data = getOccupationWrapper(
                candidate_data.resume_file, candidate_data.jobdiva_notes)
            candidate_data.occupation_title = occupation_data['occupation_title']
            candidate_data.occupation_id = occupation_data['occupation_id']

            # Step 6: Update LA area
            updateLA_Area(candidate_data)

            # Step 7: Upload candidate data to Monday.com
            createMondayItem(candidate_data)

            # Step 8: Update notes
            if candidate_data.hasNotes and candidate_data.monday_id:
                updateCandidateNotesFromJobDiva(candidate_data)

            # Step 9: Upload resume
            if candidate_data.hasResume and candidate_data.monday_id:
                uploadCandidateResume(
                    candidate_data, candidate_data.resume_file)

            # Log
            logger.info(
                f"{candidate_data.name} - Finished Processing candidate")

            # Avoid Monday rate limit
            time.sleep(0.25)

        logger.info(
            f'------------------ FINISHED {start_idx} - {end_idx} ------------------')
    # except Exception as e:
    #     print(e)


# Test Group
# Nurse Job

run(9857, 100070)

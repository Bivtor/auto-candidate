from auto_candidate import *
from Interact import *
from filewatch import *
import asyncio
import requests


async def setIsUpdating(b: bool) -> bool:
    with open(WORKING_PATH, "r") as f:
        data = json.load(f)
    data['isUpdating'] = b
    with open(WORKING_PATH, "w") as outfile:
        logger.info(f"--- updating->{b} ---")  # Log working status change
        json.dump(data, outfile)


async def checkIsUpdating() -> bool:
    f = open(WORKING_PATH)
    json_check = json.load(f)
    f.close()
    return json_check['isUpdating']


async def beginHalfAdd(candidateData: candidateData):
    """
    Creates a new candidate inside Target Folder

    Updates candidateData with folder ID

    Updates spreadsheet with known information
    """

    # Read sheet positional settings data
    f = open(SETTINGS_PATH)
    setting_data = json.load(f)

    # Set Proper Variables, Generate Title
    category = setting_data['category']
    candidateData.title = "{} {} ({})".format(candidateData.name,
                                              category, candidateData.location)
    SHEET_ID = setting_data['sheetId']
    FOLDER_PARENT = [setting_data['folderId']]  # misc default

    # Clean up Date TODO fix?
    if not (candidateData.date is None or candidateData.date == 'None'):
        candidateData.date = cleanupdate(
            candidateData.date, candidateData.source)

    # Create folder & set folder ID in candidate object
    candidate_folder_id = create_folder(candidateData.title, FOLDER_PARENT)
    candidateData.candidate_folder_id = candidate_folder_id[0]

    # Add this canddiate to the spreadsheet
    update_spreadsheet(candidateData, setting_data, SPREADSHEET_ID,
                       SHEET_ID, candidate_folder_id[1])

    return


async def finishHalfAdd(candidateData: candidateData):
    """


    """

    print("Running finishHalfAdd\n")
    # Read sheet positional settings data
    f = open(SETTINGS_PATH)
    setting_data = json.load(f)

    # Call function to finish downloading resume and update Candidate object if there is one
    if candidateData.hasResume:
        await safeCandidateUpdate(candidateData, setting_data)

    # Now that all of the candidate Data is correct, and resume is up, update everything:
        # Spreadsheet Entry
        # Folder Titles
        # Question Document
    print(candidateData)
    return

    # resume_text: str = await safeResumeDownloadHandle(dbresult, candidateData, setting_data, title)

    if resume_text != None:
        pass

    # If status is 1: We want to work on this candidate

    # Fix Phone Number and Email (Indeed Only)
    # time.sleep(2)
    # parse_resume(candidateData)
    # folder_id = "TODO"  # TODO get passed in folder ID

    # # Create Questions Document
    # category = data['category']
    # title = "{} {} ({})".format(candidateData.name,
    #                             category, candidateData.location)
    # if category == 'Therapist':
    #     create_file_Therapist(candidateData, folder_id, title)
    # elif category == 'Med Office Admin':
    #     create_file_MedOfficeAdmin(candidateData, folder_id, title)
    # elif category == 'Surgical Tech':
    #     create_file_SurgicalTech(candidateData, folder_id, title)
    # elif category == 'Recruiter':
    #     create_file_Recruiter(candidateData, folder_id, title)
    # elif category == 'Front Desk Receptionist':
    #     create_file_FrontDeskReceptionist(candidateData, folder_id, title)
    # else:
    #     create_file_general(candidateData, folder_id, title)

    # # Get License number of first (depth) entries:
    # licenselist = getLicenseInfo(candidateData.name, 5)

    # # Add License info if match to candidateData
    # curateLicenseList(licenselist, candidateData)

    # # Upload the Resume if they had one
    # if (candidateData.hasResume):
    #     # * means all if need specific format then *.csv
    #     list_of_files = glob.glob("N:\Downloads2\*")
    #     path = max(list_of_files, key=os.path.getctime)
    #     upload_basic(title, folder_id, path)

    # Move this finished candidate from 'working' to 'history'

    # return checkWorkingEmpty()


async def safeCandidateUpdate(candidateData: candidateData, setting_data: Data) -> str:
    """
    Safely download and parse the resume to ensure correctness 
    1. Establish listener on download folder
    2. Open download link
    3. Upon completion, glob newest file
    4. Return stringified resume 
    """

    # 1: Open download link (Unix)
    cmd = 'open {}'.format(candidateData.resume_download_link)  # OPEN chrome
    if os.system(cmd) != 0:
        logger.error(f"Failed to open Resume Link for {candidateData.name}")
        return f"Failed to open Resume Link for {candidateData.name}"

    logger.info("Opened resume link")

    # 2: Block until new download in folder #TODO This could cause problems

    # On Mac OS this is hindered by Python Multithreading, to fix

    handler = FileCreatedHandler(DOWNLOAD_PATH)
    handler.wait_for_file_creation()

    # 3: Get newest file, and upload resume to their folder
    list_of_files = glob.glob(DOWNLOAD_PATH + "/*")
    path = max(list_of_files, key=os.path.getctime)
    category = setting_data['category']
    candidateData.title = "{} {} ({})".format(candidateData.name,
                                              category, candidateData.location)
    candidateData.candidate_resume_id = await upload_basic(candidateData.title, [candidateData.candidate_folder_id], path)

    # 4: Get raw text from resume
    resume_text = get_raw_text(path)

    # 5: Update candidate Phone # based on regex
    parse_resume(candidateData, resume_text)

    return "Done"


def get_raw_text(directory: str) -> str:
    # Define text string and get file extension
    text = ""
    file_extension = pathlib.Path(directory).suffix.strip()

    # If .docx
    if file_extension == '.docx':
        doc = docx.Document(directory)
        text = '\s'.join([para.text for para in doc.paragraphs])
   # Else assume .pdf
    else:
        with open(directory, 'rb') as f:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(f)

            # Get the number of pages in the PDF file
            num_pages = len(pdf_reader.pages)

            # Loop through all the pages and extract the text
            for page in range(num_pages):
                # Get the page object
                pdf_page = pdf_reader.pages[page]
                # Extract the text from the page
                page_text = pdf_page.extract_text()
                # Add the page text to the overall text variable
                text += page_text
    return text


async def main():
    finishHalfAdd()


if __name__ == '__main__':
    asyncio.run(main())

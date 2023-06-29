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


async def beginHalfAdd(candidateData: candidateData, data):
    """
    Creates a new candidate inside xyz Folder and a new Questions document
    candidateData = candidate information to be inputted
    data = information about columns and sheets
    """

    # Set Proper Variables
    category = data['category']
    title = "{} {} ({})".format(candidateData.name,
                                category, candidateData.location)

    # Clean up Date
    # TODO Fix date errors in some cases
    print(f"DATE IS: {candidateData.date}")
    if not (candidateData.date is None or candidateData.date == 'None'):
        candidateData.date = cleanupdate(
            candidateData.date, candidateData.source)

    # Set Parameters
    SHEET_ID = data['sheetId']
    parents = [data['folderId']]  # misc default
    logger.info("Parents are: {} for role: {}".format(parents, category))

    # Create folder
    newParent = create_folder(title, parents)
    logger.info("Creating {}'s Folder".format(candidateData.name))
    folder_id = [newParent[0]]

    # Add current candidate to the "working on" table
    await insert_working_table_item(
        candidateData.name, newParent[0], candidateData.resume_download_link, 1, category)

    # Add this canddiate to the spreadsheet
    update_spreadsheet(candidateData, data, SPREADSHEET_ID,
                       SHEET_ID, newParent[1])


async def finishHalfAdd(candidateData: candidateData, data: Data, title: str):
    print("in finish")
    """
    High level overview:
    1. For each candidate in the database
        a. Get first candidate from working
        b. Check status of candidate
    2. If status 1:
        a. download resume
        b. parse resume
        c. upload resume
        d. find name in spreadsheet
        e. update corresponding sheet cell
        f. update db status to 2
        g. move candidate to history, 
        h. check if db is not empty and repeat
    3. If status 2:
        a. Move on to next candidate
    """
    # Step 1 get first item
    dbresult = await getFirstWorking()
    if not dbresult or dbresult is None:
        return

    # If status is not 1 (This should never be hit but it is a safety)
    if (dbresult.status != 1):
        await moveFirstToHistory(2)
        finishHalfAdd()  # call again

    # Step 2: Download/parse this person's resume

    resume_text: str = await safeResumeDownloadHandle(dbresult, candidateData, data, title)

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
    await moveFirstToHistory(2)

    return await checkWorkingEmpty()


async def safeResumeDownloadHandle(table, candidateData: candidateData, data: Data, title: str) -> str:
    """
    Safely download and parse the resume to ensure correctness 
    0. Check that we have a resume
    1. Establish listener on download folder
    2. Open download link
    3. Upon completion, glob newest file
    4. Return stringified resume 
    """

    # 0: Check that we have a resume
    if (table.resume_link != "None"):

        # 1: Open download link (Unix)
        logger.info(f"Downloading Resume for: {table.name}")
        cmd = 'open {}'.format(table.resume_link)  # OPEN chrome
        if os.system(cmd) != 0:
            return False

        # 2: Block until new download in folder #TODO This could cause problems
        handler = FileCreatedHandler(DOWNLOAD_PATH)
        handler.wait_for_file_creation()

        # 3: Glob newest file
        list_of_files = glob.glob(DOWNLOAD_PATH + "/*")
        path = max(list_of_files, key=os.path.getctime)

        title = "{} {} ({})".format(table.name,
                                    table.job_destination, candidateData.location)
        await upload_basic(title, [table.parent_id], path)

        # 4: Return raw text from resume
        return get_raw_text(path)
    return None


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
    await finishHalfAdd()


if __name__ == '__main__':
    asyncio.run(main())

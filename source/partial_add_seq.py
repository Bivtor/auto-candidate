from auto_candidate import *
from Interact import *
from filewatch import *


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
    candidateData.date = cleanupdate(candidateData.date, candidateData.source)

    # Set Parameters
    SHEET_ID = data['sheetId']
    parents = [data['folderId']]  # misc default
    logger.info("Parents are: {} for role: {}".format(parents, category))

    # Create folder
    newParent = create_folder(title, parents)
    logger.info("Creating {}'s Folder".format(candidateData.name))
    folder_id = [newParent[0]]

    await insert_working_table_item(
        candidateData.name, newParent[0], candidateData.resume_download_link, 1)

    # Call update spreadsheet function
    update_spreadsheet(candidateData, data, SPREADSHEET_ID,
                       SHEET_ID, newParent[1])

    # Check whether or not we are already working on finishing resume downloads, always try to call.
    if not await checkIsUpdating():
        await setIsUpdating(True)
        finishHalfAdd(candidateData, data)
        await setIsUpdating(False)


async def finishHalfAdd(candidateData: candidateData = None, data=None):
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

    # Step 1 get
    dbresult = await getFirstWorking()
    print(dbresult)

    # If status is not 1
    if (dbresult.status != 1):
        # Move candidate to history and try again
        # moveFirstToHistory(2)
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


async def safeResumeDownloadHandle(url: str) -> str:
    """
    Safely download and parse the resume to ensure correctness 
    1. Establish listener on download folder
    2. Open download link
    3. Upon completion, glob newest file
    4. Properly parse resume into a string
    5. Return String
    """


async def main():
    await finishHalfAdd()


if __name__ == '__main__':
    asyncio.run(main())

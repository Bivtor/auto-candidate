from pydantic import BaseModel
import PyPDF2
import re
import os
import glob
from fuzzywuzzy import fuzz
from auto_candidate import *
import pathlib


def main():
    # x = getLicenseInfo2("Dane Miller", 4)
    # print(x.headers)
    cd = candidateData(date="10/10/19", email="321", hasResume=True, license_cert="", license_expiration="",
                       location="Lompoc", name="Victor RInaldi", pagelink="https://www.vrinadi.com", phone="", source="Indeed")
    file_extension = pathlib.Path('my_file.docx').suffix
    print("File Extension: " + file_extension.strip())
    parse_resume(cd)
    print(cd)

    print()
    upload_basic(title="This si the titel", parents="Fuck you",
                 path="/Users/victorrinaldi/Desktop/auto_candidate/resumes/ResumeRobert-AlnieGarlit.pdf")


# +1(562) 395 -258


def getLicenseInfo2(name, depth) -> License:
    # Assign first and last, assuming everything but last word is first name
    first = name[:name.rfind(" ")].strip()
    last = name[name.rfind(" "):].strip()
    url = "https://search.dca.ca.gov/results"
    body = "boardCode=0&licenseType=0&licenseNumber=&firstName={}&lastName={}&registryNumber=".format(
        first, last)
    headers = {
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "if-none-match": 'W/"1e953a-vRUoGgQzuHnWBm/YM/qTtDChpnM"',
        "sec-ch-ua":
            '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            'referrer': "https://search.dca.ca.gov/",
            'referrerPolicy': "strict-origin-when-cross-origin",
            'body': "boardCode=0&licenseType=0&licenseNumber=&firstName=dane&lastName=miller&registryNumber=",
            'method': "POST",
            'mode': "cors",
            'credentials': "include",
    }

    # Collect results
    r = requests.post(url, data=body, headers=headers)
    return r
    soup = BeautifulSoup(r.text, "html.parser")

    count = 0
    licenseinfolist = list()

    # For each license we match with, collect the proper data
    for i in soup.find_all('ul', class_="actions"):
        # define items to be collected
        licensetype = ""
        licensenumber = ""
        licenseexpiration = ""
        licenselocation = ""
        if count >= depth:
            break

        # get the s = similarity value from the first li
        name_found = ""
        if i.li.h3:
            name_found = str(i.li.h3.string).lower().strip()
            name_given = (last + ", " + first).lower()
        else:
            continue

        # grab the info from the list items within each profile's ul element
        for j in i.find_all('li'):
            if str(j).find("License Number:") > 0:
                licensenumber = j.a.span.string
            if str(j).find("License Type:") > 0:
                licensetype = j.text[j.text.find(":")+2:]
            if str(j).find("Expiration Date:") > 0:
                licenseexpiration = j.text[j.text.find(":")+2:]
            if str(j).find("City:") > 0:
                licenselocation = str(j.span.text).lower()

         # append license info to return list
        licenseexpiration = cleanupdate_license(licenseexpiration)
        licenseinfolist.append(
            License(name=name_found, type=licensetype, number=licensenumber, expiration=licenseexpiration, location=licenselocation))

        count += 1

    print("Got {} licenses for {}".format(count, name))

    return licenseinfolist


def parse_resume(data: candidateData):

    # Only do this for Indeed when a resume is present
    if data.source != "Indeed" or (not data.hasResume):
        return

    # Get the directory of target file (Latest in folder )

    # PC Dir
    # list_of_files = glob.glob("N:\Downloads2\*")
    # Mac Dir (Testing)
    list_of_files = glob.glob(
        "/Users/victorrinaldi/Desktop/auto_candidate/resumes/*")

    # Target the newest file in the folder
    directory = max(list_of_files, key=os.path.getctime)

    # Define regex Patterns
    phone_regex = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    email_regex = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    # Extract text for pdf or docx
    text = ""
    file_extension = pathlib.Path(directory).suffix.strip()

    # If file type is Docx
    if file_extension == '.docx':
        doc = docx.Document(directory)
        text = '\s'.join([para.text for para in doc.paragraphs])

    else:  # Open the PDF if file type is NON docx
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

    # Use regular expressions to find phone numbers and emails in the text
    newPhone = phone_regex.findall(text)
    newEmail = email_regex.findall(text)
    if len(newPhone) > 0:
        data.phone = newPhone[0]
    if len(newEmail) > 0:
        data.email = newEmail[0]

        # Print the results for the current PDF file
    print("Altered Phone/Email for: {} in directory: {}".format(data.name, directory))


def upload_basic(title, parents, path):
    """Insert new file.
    Returns : Id's of the file uploaded

    Load pre-authorized user credentials from the environment.
    for guides on implementing OAuth2 for the application.
    """

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': title, 'parents': parents}

        # Determine if file is pdf or docx and set media accoordingly
        file_extension = pathlib.Path(path).suffix.strip()
        media = media = MediaFileUpload(
            path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document') if file_extension == ".docx" else MediaFileUpload(
            path, mimetype='application/pdf')

        # Execute upload
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File ID: {file.get("id")}')
        print("Uploaded Resume Successfully")
        return file.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None


if __name__ == "__main__":
    main()

from twilio.rest import Client
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import date, datetime
from fuzzywuzzy import fuzz
from paths import *
from bs4 import BeautifulSoup

import time
import os
import os.path
import json
import re


import requests

# Amazon SES Send Email info
import boto3
import logging

# import boto3
from botocore.exceptions import ClientError
from botocore.config import Config


load_dotenv(dotenv_path=ENV_PATH)

# Logging formation
logger = logging.getLogger('logger')

# Set logger level
logger.setLevel(logging.DEBUG)

# create handler
handler = logging.FileHandler(LOGGER_PATH)

# set handler level
handler.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# set formatter
handler.setFormatter(formatter)

# add handler to logger
logger.addHandler(handler)


class Data(BaseModel):
    password: str
    action: str
    occupation: str
    group: str
    link: str = ""
    start: int = 2
    end: int = 1000
    message: str = ""
    messageType: str = ""

    # Sheet/Folder containment info
    isSheet: bool = False
    isFolder: bool = False
    sheetId: str | None = None
    folderId: str | None = None

    # Sheet position info
    positions: list[str] = []
    err: str | None = None


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
    monday_id: str | None
    notes_id: str | None


class License(BaseModel):
    name: str
    type: str
    number: str
    expiration: str
    location: str


def cleanupdate_license(date):
    date2 = ""

    def findMonth(month: str):

        return date[date.find(" ")+1:date.find(",")] + "/" + date[date.find("202")+2:date.find("202")+4]

    if date.find("Jan"):
        date2 += "1/"
        date2 += findMonth("Jan")
    elif date.find("Feb"):
        date2 += "2/"
        date2 += findMonth("Feb")
    elif date.find("Mar"):
        date2 += "3/"
        date2 += findMonth("Mar")
    elif date.find("Apr"):
        date2 += "4/"
        date2 += findMonth("Apr")
    elif date.find("May"):
        date2 += "5/"
        date2 += findMonth("May")
    elif date.find("Jun"):
        date2 += "6/"
        date2 += findMonth("Jun")
    elif date.find("Jul"):
        date2 += "7/"
        date2 += findMonth("Jul")
    elif date.find("Aug"):
        date2 += "8/"
        date2 += findMonth("Aug")
    elif date.find("Sep"):
        date2 += "9/"
        date2 += findMonth("Sep")
    elif date.find("Oct"):
        date2 += "10/"
        date2 += findMonth("Oct")
    elif date.find("Nov"):
        date2 += "11/"
        date2 += findMonth("Nov")
    elif date.find("Dec"):
        date2 += "12/"
        date2 += findMonth("Dec")
    date = date2
    return date


def cleanupdate(date: str, source: str):
    # If the source is ZipRecruiter
    if source == "ZipRecruiter":
        date2: str = ""

        def findMonth(month: str):
            return date[date.find(month)+4:date.find(",")] + "/" + date[date.find("202")+2:date.find("202")+4]
        if date.find("Jan") > 0:
            date2 += "1/"
            date2 += findMonth("Jan")
        elif date.find("Feb") > 0:
            date2 += "2/"
            date2 += findMonth("Feb")
        elif date.find("Mar") > 0:
            date2 += "3/"
            date2 += findMonth("Mar")
        elif date.find("Apr") > 0:
            date2 += "4/"
            date2 += findMonth("Apr")
        elif date.find("May") > 0:
            date2 += "5/"
            date2 += findMonth("May")
        elif date.find("Jun") > 0:
            date2 += "6/"
            date2 += findMonth("Jun")
        elif date.find("Jul") > 0:
            date2 += "7/"
            date2 += findMonth("Jul")
        elif date.find("Aug") > 0:
            date2 += "8/"
            date2 += findMonth("Aug")
        elif date.find("Sep") > 0:
            date2 += "9/"
            date2 += findMonth("Sep")
        elif date.find("Oct") > 0:
            date2 += "10/"
            date2 += findMonth("Oct")
        elif date.find("Nov") > 0:
            date2 += "11/"
            date2 += findMonth("Nov")
        elif date.find("Dec") > 0:
            date2 += "12/"
            date2 += findMonth("Dec")
        date = date2
        return date

    # If the source is indeed do this
    elif source == "Indeed":
        date_obj = datetime.strptime(date, '%b %d, %Y')
        return date_obj.strftime('%m/%d/%Y')


def parse_resume(candidateData: candidateData, text):

    # Only do this for Indeed when a resume is present
    if candidateData.source != "Indeed" or (not candidateData.hasResume):
        logger.info(
            f"{candidateData.name} - Choose not to parse resume (Non Indeed Candidate) ")
        return

    # Define regex Patterns
    phone_regex = re.compile(r"\(?\d{3}\)?[-.\s]*?\d{3}[-.\s]*?\d{4}")

    email_regex = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    # Use regular expressions to find phone numbers and emails in the text
    newPhone = phone_regex.findall(text)
    newEmail = email_regex.findall(text)

    # Update values if found
    if len(newPhone) > 0:
        candidateData.phone = newPhone[0]
        logger.info(f"{candidateData.name} - Updated Phone number from resume")
    if len(newEmail) > 0:
        candidateData.email = newEmail[0]
        logger.info(f"{candidateData.name} - Updated Email from resume")

    return


def getLicenseInfo(name, depth) -> License:
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

    logger.info("Got {} licenses for {}".format(count, name))

    return licenseinfolist


class SesDestination:
    """Contains data about an email destination."""

    def __init__(self, tos, ccs=None, bccs=None):
        """
        :param tos: The list of recipients on the 'To:' line.
        :param ccs: The list of recipients on the 'CC:' line.
        :param bccs: The list of recipients on the 'BCC:' line.
        """
        self.tos = tos
        self.ccs = ccs
        self.bccs = bccs

    def to_service_format(self):
        """
        :return: The destination data in the format expected by Amazon SES.
        """
        svc_format = {'ToAddresses': self.tos}
        if self.ccs is not None:
            svc_format['CcAddresses'] = self.ccs
        if self.bccs is not None:
            svc_format['BccAddresses'] = self.bccs
        return svc_format


class SesMailSender:
    """Encapsulates functions to send emails with Amazon SES."""

    def __init__(self, ses_client):
        """
        :param ses_client: A Boto3 Amazon SES client.
        """
        self.ses_client = ses_client

    def send_email(self, source, destination, subject, text, html, name, category, email, reply_tos=None):
        """
        Sends an email.

        Note: If your account is in the Amazon SES  sandbox, the source and
        destination email accounts must both be verified.

        :param source: The source email account.
        :param destination: The destination email account.
        :param subject: The subject of the email.
        :param text: The plain text version of the body of the email.
        :param html: The HTML version of the body of the email.
        :param reply_tos: Email accounts that will receive a reply if the recipient
                          replies to the message.
        :return: The ID of the message, assigned by Amazon SES.
        """
        send_args = {
            'Source': source,
            'Destination': destination.to_service_format(),
            'Message': {
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': text}}}}
        if reply_tos is not None:
            send_args['ReplyToAddresses'] = reply_tos
        try:
            response = self.ses_client.send_email(**send_args)
            message_id = response['MessageId']
            logger.info("Sent mail %s from %s to %s.",
                        message_id, source, destination.tos)

            # Not writing json we dont care
            # write_json({"name": name, "job": category,
            #             "email": email, "response_code": response, 'body': text})
            logger.info(
                "Successfully sent email to: {} -> ".format(name, destination.tos[0]))
        except ClientError as err:
            logger.error(
                "Invalid email destination for: {} -> {}".format(name, destination.tos[0]))

            # Not writing json we dont care
            # write_json({"name": name, "job": category,
            #             "email": email, "response_code": str(err.response)})
        else:
            return message_id


def sendTwilioText(name: str, number: str, body: str):
    # Find your Account SID and Auth Token and Message
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    service_id = os.environ['TWILIO_SERVICE_ID']

    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            messaging_service_sid=service_id,
            body=body,
            to=number,
        )
        # Update record that text has been sent / status of return
        # Not writing json we dont care
        # write_json({"name": name, "body": message.body, "number": number,
        #            "date": str(date.today()), "messageID": message.sid, "failed": False})
        logger.info("\nSent message to {} with number: {}".format(name, number))
        return True
    except:
        # Not writing json we dont care
        # write_json({"name": name, "body": body,
        #            "number": number, "messageID": "null", "failed": True})
        logger.info("\nCould not send message to: {} -> {}".format(
            name, number))
        return False


def sendAWSEmail(name: str, email: str, body: str, category: str, mailsender, source: str):
    # Create destination type
    destination = SesDestination(tos=[email])

    # Send mail and log response
    mailsender.send_email(
        destination=destination, subject="New Job Opportunity from Solution Based Therapeutics", text=body, source=source, html="", name=name, category=category, email=email)


def write_json(new_data, filename=RECORDS_PATH):
    with open(filename, 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data
        file_data["records"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)


def curateLicenseList(licenselist: list[License], candidateData: candidateData):
    # For each match that we get
    for match in licenselist:
        # if fuzzywuzzy location similarity score is high enough, return proper info
        if fuzz.partial_ratio(candidateData.location.lower(), match.location.lower()) >= 75:
            # Assign License Name - Number
            candidateData.license_cert = "{} - {}".format(
                match.type, match.number)
            # Assign License Expiration
            candidateData.license_expiration = match.expiration
            return  # Break


def find_closest_string(query, string_list):
    max_similarity = 0
    closest_string = None
    for string in string_list:
        similarity = fuzz.ratio(query, string)
        if similarity > max_similarity:
            max_similarity = similarity
            closest_string = string
    if max_similarity < .3:
        closest_string = "Pre-screening"
    return closest_string


def main():
    pass


if __name__ == '__main__':
    main()

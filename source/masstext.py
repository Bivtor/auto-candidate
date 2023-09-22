from auto_candidate import logger, Data
from update_monday import getGroupMessageInfo, updateCandidateTextStatus
from paths import RECEIPT_PATH
import os
import time

# import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import boto3

# import Twilio
from twilio.rest import Client


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

    def send_email(self, source, destination, subject, text, reply_tos=None):
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

            # Log
            logger.info(
                f"Sent mail {message_id} from {source} to {destination.tos}"
            )

            # Update Receipt
            append_text_to_file(
                RECEIPT_PATH, f"Successfully sent email from {source} to {destination.tos}\n\n"
            )

        except ClientError as err:
            logger.error(err)

            # Log
            logger.error(
                f"Invalid email destination: {destination.tos}")

            # Update Receipt
            append_text_to_file(
                RECEIPT_PATH, f"Invalid email destination: {destination.tos}\n\n"
            )

        else:
            return message_id


def sendText(name: str, number: str, body: str):
    """
    Message body should be formatted already, 'name' is just for logging
    """
    # Find your Account SID and Auth Token and Message
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    service_id = os.environ['TWILIO_SERVICE_ID']

    # Create Twilio Client Object
    client = Client(account_sid, auth_token)

    try:
        # Send message
        message = client.messages.create(
            messaging_service_sid=service_id,
            body=body,
            to=number,
        )

        # Log
        logger.info(
            f"{name} - Successfully Sent Message to Twilio for {number}")

        # Update Receipt File
        append_text_to_file(
            RECEIPT_PATH, f"{name} - Successfully Sent Message to Twilio at {number}\n"
        )

    except:
        # Log
        logger.info(f"{name} - Failed to Send Message to Twilio for {number}")

        # Update Receipt File
        append_text_to_file(
            RECEIPT_PATH, f"{name} - Failed to Send Message to Twilio for {number}\n"
        )

    return


def sendEmail(source: str, destination_email: str,  subject: str, body: str):
    """
    Helper Method that sends an email using Amazon AWS Client
    """

    # Remove Whitespace or \n characters from email string
    email = destination_email.replace(" ", "").replace("\n", "")


    # Create destination type
    destination = SesDestination(tos=[email])

    # Create boto3 Client
    client = boto3.client('ses', region_name="us-west-1", aws_access_key_id=os.getenv(
        'aws_access_key_id'), aws_secret_access_key=os.environ.get('aws_secret_access_key'))

    # Create Mailsender
    mailsender = SesMailSender(ses_client=client)

    # Send mail and log response
    mailsender.send_email(
        source=source,
        destination=destination,
        subject=subject,
        text=body
    )
    return


def send_test_mailtext(data: Data):
    """
    Sends an email/text to the test_phone and test_email fields
    """

    # Generate body with test name "Bob Odenkirk"
    message = data.message.replace("[candidate_name]", "Bob Odenkirk")

    # Assign Subject
    subject = "New Job Opportunity from Solution Based Therapeutics"


    # Call Email Send (Helper Function)
    sendEmail(destination_email=data.test_email,
              body=message,
              source=data.source_email,
              subject=subject)

    # Call Text Send (Helper Function)
    sendText(name="Bob Odenkirk (Test)",
             number=data.test_phone,
             body=message)

    return


def send_group_mail_function(data: Data):
    """
    Send an email/text to everyone who has a status marked "Message Scheduled" in a specified group on Monday
    """

    # Clear receipt file
    clear_text_in_file(RECEIPT_PATH)

    # Add opener to Receipt file
    append_text_to_file(RECEIPT_PATH, "Text/Mail Order Receipt:\n\n")

    # Get Monday Info
    monday_info = getGroupMessageInfo(data)

    # Call driver Function
    process_group_mail_data(web_input_data=data, monday_input_data=monday_info)

    # Send Receipt Emails
    send_receipt_email('gabe@solutionbasedtherapeutics.com')
    send_receipt_email('stephanie@solutionbasedtherapeutics.com')

    return


def process_group_mail_data(web_input_data: Data, monday_input_data: dict):
    """
    This function will recieve all of the data that is needed to send messages
    For each peson in the group:
        Checks if they should be texted
        If they should: 
            Format message with their name
            Send Text
            Send Email
            Update their Monday status to confirm that they have been texted
            continue
    """
    # Count Messages Sent
    Messages_Sent = 0

    # Target the proper list of candidates from the monday_input_data return
    candidate_list = monday_input_data['data']['boards'][0]['groups'][0]['items']

    # Iterate over data
    for person in candidate_list:
        # Skip if they should do not need to be messaged
        if (person['column_values'][2]['text'] != "Message Scheduled"):
            continue

        # Format data for name of person to be messaged
        message = web_input_data.message.replace(
            "[candidate_name]", person.get("name", "Candidate"))

        # Assign Subject
        subject = "New Job Opportunity from Solution Based Therapeutics"

        # Send Text
        sendText(name=person.get("name", "Candidate"),
                 number=person['column_values'][0]['text'],
                 body=message)

        # Send Email
        sendEmail(destination_email=person['column_values'][1]['text'],
                  body=message,
                  source=web_input_data.source_email,
                  subject=subject)

        # Update Monday ID of Candidate to "Messaged"
        updateCandidateTextStatus(
            candidate_id=person['id'], log_name=person['name'], new_status="Message Sent")

        # Wait a tiny bit to prevent using API too fast
        time.sleep(.01)

        Messages_Sent += 1

    # Log Finish
    logger.info(
        f"{web_input_data.group} - Finished Sending {Messages_Sent} Messages")

    # Add Finish to Receipt
    append_text_to_file(
        RECEIPT_PATH, f"\nFinished Sending {Messages_Sent} Messages to {web_input_data.group} Group\n")

    return


def send_receipt_email(dest):
    """
    Sends the contents of the receipt file to Employers
    """

    # Retrieve text from file
    receipt = retrieve_file_contents(RECEIPT_PATH)

    # Send email with receipt
    # TODO Change destination emails
    sendEmail(source='info@solutionbasedtherapeutics.com',
              destination_email=dest,
              subject='Receipt of Text/Email Order',
              body=receipt)


def retrieve_file_contents(file_path: str) -> str:
    """
    Retrieve receipt email file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(
            f"An error occurred while reading the file '{file_path}': {str(e)}")
        return None


def append_text_to_file(file_path, text):
    """
    Appends text to receipt file
    """
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(text)
    except Exception as e:
        print(f"An error occurred while appending to '{file_path}': {str(e)}")


def clear_text_in_file(file_path):
    """
    Clear receipt file
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('')
        print(f"Text cleared from '{file_path}' successfully.")
    except Exception as e:
        print(f"An error occurred while clearing '{file_path}': {str(e)}")

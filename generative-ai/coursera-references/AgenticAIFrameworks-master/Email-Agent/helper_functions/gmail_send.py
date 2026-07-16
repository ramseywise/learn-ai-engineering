# Gmail Send Module
# Functions for sending emails with attachments

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import os


def send_email(service, to, subject, body, body_type='plain', attachment_paths=None):
    """
    Send an email with optional attachments.
    
    Args:
        service: Gmail API service object
        to (str): Recipient email address
        subject (str): Email subject
        body (str): Email body
        body_type (str): Body type ('plain' or 'html', default: 'plain')
        attachment_paths (list): List of file paths to attach
    
    Returns:
        dict: Response from Gmail API
    """
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject

    if body_type.lower() not in ['plain', 'html']:
        raise ValueError("body_type must be either plain or html")

    message.attach(MIMEText(body, body_type.lower()))

    if attachment_paths:
        for attachment_path in attachment_paths:
            if os.path.exists(attachment_path):
                filename = os.path.basename(attachment_path)

                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)

                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )

                message.attach(part)
            else:
                raise FileNotFoundError(f"File not found - {attachment_path}")

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    sent_message = service.users().messages().send(
        userId='me',
        body={'raw': raw_message}
    ).execute()

    return sent_message
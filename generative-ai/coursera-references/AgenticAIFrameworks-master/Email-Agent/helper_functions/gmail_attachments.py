# Gmail Attachments Module
# Functions for downloading email attachments

import os
import base64


def download_attachments_parent(service, user_id, msg_id, target_dir):
    """
    Download attachments from a single email message.
    
    Args:
        service: Gmail API service object
        user_id (str): User ID
        msg_id (str): Message ID
        target_dir (str): Directory to save attachments
    """
    message = service.users().messages().get(
        userId=user_id,
        id=msg_id
    ).execute()

    for part in message['payload'].get('parts', []):
        if part.get('filename'):
            att_id = part['body']['attachmentId']
            att = service.users().messages().attachments().get(
                userId=user_id,
                messageId=msg_id,
                id=att_id
            ).execute()

            data = att['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            file_path = os.path.join(target_dir, part['filename'])

            print('Saving attachment to:', file_path)
            with open(file_path, 'wb') as f:
                f.write(file_data)


def download_attachments_all(service, user_id, msg_id, target_dir):
    """
    Download attachments from all messages in a thread.
    
    Args:
        service: Gmail API service object
        user_id (str): User ID
        msg_id (str): Thread ID (using message ID from thread)
        target_dir (str): Directory to save attachments
    """
    thread = service.users().threads().get(
        userId=user_id,
        id=msg_id
    ).execute()

    for message in thread['messages']:
        for part in message['payload'].get('parts', []):
            if part.get('filename'):
                att_id = part['body']['attachmentId']
                att = service.users().messages().attachments().get(
                    userId=user_id,
                    messageId=message['id'],
                    id=att_id
                ).execute()

                data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                file_path = os.path.join(target_dir, part['filename'])

                print('Saving attachment to:', file_path)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
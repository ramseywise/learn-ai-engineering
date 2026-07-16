# Gmail API Helper Package
# Import main functions for easy access

from .gmail_auth import init_gmail_service
from .gmail_fetch import get_email_messages, get_email_message_details
from .gmail_send import send_email
from .gmail_attachments import download_attachments_parent, download_attachments_all
from .gmail_search import search_emails, search_email_conversations

__all__ = [
    'init_gmail_service',
    'get_email_messages',
    'get_email_message_details',
    'send_email',
    'download_attachments_parent',
    'download_attachments_all',
    'search_emails',
    'search_email_conversations'
]
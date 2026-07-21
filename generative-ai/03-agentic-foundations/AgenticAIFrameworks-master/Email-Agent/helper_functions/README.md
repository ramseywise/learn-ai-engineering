# Gmail API Helper Functions

This package provides helper functions for interacting with the Gmail API, including authentication, fetching emails, sending emails with attachments, downloading attachments, and searching emails.

## Prerequisites

- Python 3.10.7 or greater
- A Google Cloud project
- A Google account with Gmail enabled

## Setup Steps

1. **Create Google Cloud Project**

   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Gmail API**

   - In the Google Cloud Console, go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it

3. **Configure the OAuth consent screen**

   - Go to "APIs & Services" > "OAuth consent screen"
   - Configure the consent screen for your application

4. **Authorize credentials for a desktop application**

   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Select "Desktop application" as the application type

5. **Create Client**

   - In the Credentials page, find your OAuth 2.0 Client ID
   - Download the JSON file and rename it to `client_secrets.json`
   - Move the file to your working directory

6. **Install required libraries**
   ```
   pip install -r requirements.txt
   ```

## File Structure

- gmail_auth.py - Authentication and service initialization functions
- gmail_fetch.py - Email fetching and message detail extraction
- gmail_send.py - Email sending with attachment support
- gmail_attachments.py - Attachment download functions
- gmail_search.py - Email and conversation search functions
- init.py - Package initialization with main function exports
- requirements.txt - Python dependencies
- README.md - Setup instructions and usage guide

## Usage

Import the package and use the functions:

```python
from email_poc import init_gmail_service, get_email_messages, send_email

# Initialize service
service = init_gmail_service('client_secrets.json')

# Fetch emails
messages = get_email_messages(service, max_results=10)

# Send email
response = send_email(service, 'recipient@example.com', 'Subject', 'Body')
```

## Available Functions

- `init_gmail_service()`: Initialize Gmail API service
- `get_email_messages()`: Fetch emails from inbox or specific folder
- `get_email_message_details()`: Get detailed information about a specific email
- `send_email()`: Send emails with optional attachments
- `download_attachments_parent()`: Download attachments from a single email
- `download_attachments_all()`: Download attachments from all emails in a thread
- `search_emails()`: Search for emails using Gmail query syntax
- `search_email_conversations()`: Search for email conversations

## Gmail Search Query Examples

- `from:sender@example.com`
- `to:recipient@example.com`
- `subject:"important meeting"`
- `after:2023/01/01 before:2023/12/31`
- `has:attachment`
- `is:starred`

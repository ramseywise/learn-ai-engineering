# Gmail Search Module
# Functions for searching emails and conversations


def search_emails(service, query, user_id='me', max_results=5):
    """
    Search for emails using Gmail query syntax.
    
    Args:
        service: Gmail API service object
        query (str): Gmail search query
        user_id (str): User ID (default: 'me')
        max_results (int): Maximum number of results (default: 5)
    
    Returns:
        list: List of message objects matching the query
    """
    messages = []
    next_page_token = None

    while True:
        result = service.users().messages().list(
            userId=user_id,
            q=query,
            maxResults=min(500, max_results - len(messages)) if max_results else 500,
            pageToken=next_page_token
        ).execute()

        messages.extend(result.get('messages', []))
        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(messages) >= max_results):
            break

    return messages[:max_results] if max_results else messages


def search_email_conversations(service, query, user_id='me', max_results=5):
    """
    Search for email conversations (threads) using Gmail query syntax.
    
    Args:
        service: Gmail API service object
        query (str): Gmail search query
        user_id (str): User ID (default: 'me')
        max_results (int): Maximum number of results (default: 5)
    
    Returns:
        list: List of thread objects matching the query
    """
    conversations = []
    next_page_token = None

    while True:
        result = service.users().threads().list(
            userId=user_id,
            q=query,
            maxResults=min(500, max_results - len(conversations)) if max_results else 500,
            pageToken=next_page_token
        ).execute()

        conversations.extend(result.get('threads', []))
        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(conversations) >= max_results):
            break

    return conversations[:max_results] if max_results else conversations
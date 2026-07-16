# Agentic Email Workflow

A Streamlit-based chatbot that answers course-related questions and can send emails to the professor using LangGraph agents and Gmail API.

---

## Directory Structure

```
Email-Agent/
│
├── app.py # Main Streamlit application
├── agent.py # LangGraph agent with email tool
├── course_data.py # Course knowledge base
├── requirements.txt # Python dependencies
├── .env # Environment variables (not in repo)
├── .env.example # Template for .env
├── .gitignore # Git ignore rules
├── client_secrets.json # Google OAuth (not in repo)
│
├── helper_functions/ # Gmail API integration (provided)
│ ├── **init**.py
│ ├── gmail_auth.py # OAuth authentication
│ ├── gmail_send.py # Email sending
│ ├── gmail_fetch.py # Email retrieval
│ ├── gmail_attachments.py # Attachment handling
│ ├── gmail_search.py # Email search
│ ├── requirements.txt
│ └── README.md
│
├── README.md # Main documentation
├── QUICKSTART.md # Fast setup guide
├── DEPLOYMENT.md # Streamlit Cloud deployment
└── PROJECT_SUMMARY.md # This file
```

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
│  - Chat interface                                       │
│  - File upload                                          │
│  - Sidebar with course info                             │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│                  LangGraph Agent                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Agent Node                                     │   │
│  │  - Receives user question                       │   │
│  │  - Accesses course context                      │   │
│  │  - Decides: Answer or Email                     │   │
│  └─────────────┬───────────────────────────────────┘   │
│                │                                       │
│                ▼                                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Tool: send_email_to_professor                  │   │
│  │  - Composes email                               │   │
│  │  - Attaches files                               │   │
│  │  - Calls Gmail API                              │   │
│  └─────────────┬───────────────────────────────────┘   │
└────────────────┼───────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                 Gmail API Service                       │
│  - OAuth 2.0 authentication                             │
│  - Email sending with attachments                       │
│  - Helper functions wrapper                             │
└─────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Professor's Gmail                          │
│  Receives: advait.shinde@sjsu.edu                       │
└─────────────────────────────────────────────────────────┘
```

### Steps to run:

1. Dependencies

```
pip install -r requirements.txt
```

2. Create a .env file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here
```

3.  Configure Google Gmail API

- Go to Google Cloud Console
- Enable Gmail API
- Create OAuth 2.0 credentials (Desktop application)
- Download as client_secrets.json

4. Run Locally

```
streamlit run app.py
```

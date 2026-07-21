import os

_USE_AZURE = all(
    [
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        os.getenv("AZURE_OPENAI_API_VERSION"),
    ]
)

_USE_BING = all([os.getenv("BING_SUBSCRIPTION_KEY")])

# ensure that all required environment variables are set
if not _USE_AZURE:
    raise Exception("Azure OpenAI environment variables not set.")

if not _USE_BING:
    raise Exception(
        "Bing Search API environment variables not set. Please set BING_SUBSCRIPTION_KEY and optionally BING_SEARCH_URL."
    )

POSTGRES_URI = os.getenv(
    "POSTGRES_URI",
    # Example URI for local PostgreSQL database
    "postgresql://postgres:postgres@localhost:5432/postgres?sslmode=disable",
)
_USE_POSTGRES_CHECKPOINTER = bool(os.getenv("POSTGRES_URI"))

SQLITE_DB_LOCAL_PATH = os.getenv(
    "SQLITE_DB_LOCAL_PATH",
    # Example URI for local SQLite database
    "state_db/example.db",
)
_USE_SQLITE_CHECKPOINTER = bool(os.getenv("SQLITE_DB_LOCAL_PATH"))

API_VERSION = "v1"
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
BING_SEARCH_URL = os.getenv("BING_SEARCH_URL", "https://api.bing.microsoft.com/v7.0/search")
BING_SUBSCRIPTION_KEY = os.getenv("BING_SUBSCRIPTION_KEY", "")
CRAWLER_URL = os.getenv("CRAWLER_URL", "")
DEFAULT_AGENT = os.getenv("DEFAULT_AGENT", "simple-search")

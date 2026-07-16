from langchain_openai import AzureChatOpenAI

from src.config import (
    _USE_AZURE,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME,
)

if _USE_AZURE:
    llm = AzureChatOpenAI(
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
        temperature=0,
    )

from pydantic import BaseModel, Field


class BingSearchResult(BaseModel):
    body: str
    href: str
    title: str
    index: int
    content: str | None = None  # Content scraped from the webpage


class SearchDecision(BaseModel):
    """Structured output for the decision LLM."""

    should_search: bool = Field(description="True if the agent should perform a web search for this query.")

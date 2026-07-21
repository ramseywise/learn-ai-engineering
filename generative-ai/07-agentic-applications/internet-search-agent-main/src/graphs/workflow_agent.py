import ast
import json
from datetime import datetime

import requests
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph

from src import config
from src.clients.llm_client import llm
from src.clients.search_client import bing_search
from src.models.schemas import OutlinePlan
from src.models.search_schemas import BingSearchResult, SearchDecision


class WorkflowState(MessagesState):
    """Graph state propagated between nodes."""

    # --- planning ---
    outline: list[str]
    current_idx: int = 0
    # --- per-section work ---
    search_results: list[BingSearchResult]
    section_drafts: list[str]
    should_search: bool


###############################################################################
# Graph nodes
###############################################################################
def decide_search(state: WorkflowState) -> dict:
    """Classifier that decides—via structured output—whether to issue a web search."""
    # the reason that i think having a decision node here is better compared than to just define a search tool is that i can have more control over the search node
    # and there in the search node you can formulate the search query separetly but then when you define a a search tool you have to define the search query in the tool itself
    # and that is not very flexible - causes problems because then the llm will get a log of instructions
    system_msg = SystemMessage(
        content="You are a classifier that must decide whether the user's question requires a live web search."
    )
    user_msg = HumanMessage(content=f"Conversation history: {state['messages']}")

    structured_llm = llm.with_structured_output(SearchDecision)
    response = structured_llm.invoke([system_msg, user_msg])
    
    # Handle both dict and object responses
    decision = SearchDecision(**response) if isinstance(response, dict) else response

    return {"should_search": decision.should_search}


def plan_outline(state: WorkflowState) -> dict:
    topic = state["messages"][-1].content  # last user msg = topic
    prompt = (
        "You are a senior sustainability analyst. "
        f"Write a 3 bullet point high-level outline for an in-depth report on:\n«{topic}»\n"
        "Return ONLY a JSON array of section titles."
    )
    structured_llm = llm.with_structured_output(OutlinePlan)
    outline_plan = structured_llm.invoke(prompt)
    
    # Handle both dict and object responses
    if isinstance(outline_plan, dict):
        outline_plan = OutlinePlan(**outline_plan)
    
    return {"outline": outline_plan.outline, "current_idx": 0}


def _crawl_single_url(url, base_url):
    """Helper function to crawl a single URL and return its content.

    Args:
        url (str): The URL to crawl
        base_url (str): The base URL of the crawler service

    Returns:
        str: The extracted markdown content or an error message
    """
    if not url:
        return ""

    try:
        request_data = {"url": url, "f": "fit", "q": None, "c": "0"}

        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{base_url}/md", json=request_data, headers=headers)
        response.raise_for_status()
        result = response.json()

        # Extract markdown content if available
        if result and result.get("success", False):
            return result.get("markdown", "")
    except requests.exceptions.RequestException as e:
        return f"Failed to crawl content: Network error - {str(e)}"
    except ValueError as e:  # JSON parsing error
        return f"Failed to crawl content: Invalid response format - {str(e)}"
    except Exception as e:
        return f"Failed to crawl content: Unexpected error - {str(e)}"

    return ""  # Default return if no content was extracted


def _sync_crawl_urls(results_list):
    """Synchronously crawl URLs from search results using crawl4ai.

    Args:
        results_list (list): List of search results with URLs to crawl

    Returns:
        list: Normalized search results with crawled content
    """
    if not results_list:
        return []

    normalized_results = []
    base_url = config.CRAWLER_URL

    for i, item in enumerate(results_list):
        url = item.get("link", "")
        content = _crawl_single_url(url, base_url) if url else ""

        normalized_results.append(
            BingSearchResult(
                body=item.get("snippet", ""),
                href=url,
                title=item.get("title", ""),
                index=i + 1,  # Adding 1-based index for citation purposes
                content=content,  # Add the scraped content
            )
        )

    return normalized_results


def search_section(state: WorkflowState) -> dict:
    section_title = state["outline"][state["current_idx"]]
    system_msg = SystemMessage(
        content=f"You are a search assistant. Formulate a search query for Bing based on the conversation history. The search query must be focused on {section_title}."
    )
    user_msg = HumanMessage(content=f"Conversation history: {state['messages']}")
    search_query = llm.invoke([system_msg, user_msg])

    # Initial search attempt
    results_json = bing_search.invoke(search_query.content)
    results_list = ast.literal_eval(results_json)

    # Retry logic if initial search fails
    retry_count = 0
    max_retries = 2

    while retry_count < max_retries and (
        not results_list
        or ("Results" in results_list and results_list["Results"] == "No good Bing Search Result was found")
    ):
        # Create a more specific search query by reformulating with more context
        retry_system_msg = SystemMessage(
            content=f"You are a search assistant. The previous search query for '{section_title}' returned no good results. "
            f"This is retry attempt {retry_count + 1} of {max_retries}. "
            f"Create a more specific and detailed search query for Bing that will yield better results. "
            f"Consider using more technical terms, alternative keywords, or rephrasing the query entirely."
        )
        retry_context_msg = HumanMessage(
            content=f"Previous failed query: {search_query.content}\nSection title: {section_title}\nConversation history: {state['messages']}"
        )
        new_search_query = llm.invoke([retry_system_msg, retry_context_msg])

        # Execute the retry search
        results_json = bing_search.invoke(new_search_query.content)
        results_list = ast.literal_eval(results_json)

        # Update the search query for the next potential retry
        search_query = new_search_query
        retry_count += 1

    # If we still have no results after retry
    if not results_list or (
        "Results" in results_list and results_list["Results"] == "No good Bing Search Result was found"
    ):
        return {
            "search_results": [
                BingSearchResult(
                    body="No search results found after retry",
                    href="",
                    title="No Results",
                    index=1,
                    content="No content could be found for this section. The section will be drafted using general knowledge.",
                )
            ],
        }

    normalized_results = _sync_crawl_urls(results_list)
    return {"search_results": normalized_results}


def draft_section(state: WorkflowState) -> dict:
    section_title = state["outline"][state["current_idx"]]
    context_block = ""
    search_results = state.get("search_results", [])
    if len(search_results) > 0:
        results_for_json = [result.model_dump() for result in search_results]
        context_block = f"Search Results:\\n{json.dumps(results_for_json)}"
    prompt = """
        Write a 200-300 word section titled "{section_title}". 
        Use ONLY the sources provided below and cite each claim inline with [href] at the end of the claim
        For example:
        According to the search results, the sky is blue [https://example.com].

        The search results include both snippets (body) and full content from the webpage.
        Use the full content when available to provide more detailed and accurate information.

        Following search results are available:
        {search_results}
        """
    prompt = prompt.format(section_title=section_title, search_results=context_block)
    draft = llm.invoke(prompt).content.strip()
    # Check if section_drafts exists in state before appending
    if "section_drafts" in state:
        return {"section_drafts": state["section_drafts"] + [draft]}
    else:
        return {"section_drafts": [draft]}


def advance_index(state: WorkflowState) -> dict:
    """Increment the section pointer by one and clear search results."""
    return {"current_idx": state["current_idx"] + 1, "search_results": []}


def should_continue(state: WorkflowState) -> str:
    """Return 'continue' if more sections remain, else 'finish'."""
    next_idx = state["current_idx"] + 1
    return "continue" if next_idx < len(state["outline"]) else "finish"


def compile_report(state: WorkflowState) -> dict:
    joined = "\n\n".join(state["section_drafts"])
    intro = (
        "You are the report editor.  Write a 2-3 sentence introduction for the "
        "report below, then append the compiled sections unchanged.\n\n"
    )
    compiled_report = llm.invoke(intro + joined)
    return {"messages": [compiled_report], "search_results": [], "outline": [], "current_idx": 0, "section_drafts": []}


def generate_answer(state: WorkflowState) -> dict:
    messages = state["messages"]
    system_message = """
    You are a sustainability-focused digital assistant. Your primary task is to support in-depth research and answer questions related to sustainability, environmental impact, green technologies, industry practices, and corporate sustainability reports.
    
    If a query is ambiguous or only partially relevant, ask a clarifying question to guide the conversation back to sustainability.
    
    When declining a query, do so professionally and concisely. Keep your tone helpful and respectful. Here are some example behaviors:
    - If the user asks "How tall is the Eiffel Tower?" reply with:
        > I'm here to assist with sustainability-related questions. Feel free to ask about environmental topics or industry sustainability practices.

    - If the user says "Tell me a joke", respond with:
        > My focus is on providing accurate and helpful sustainability insights. Let me know if you’d like to explore a topic in that area.

    Do not search the internet or generate long replies for unrelated queries. Your focus is always sustainability.
    Today is {today_date_time}.
    """.format(today_date_time=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))

    # after the search results are added we need to clear them from the state
    invoked_result = llm.invoke([SystemMessage(content=system_message)] + messages)
    # Clear search results from the state
    return {"messages": [invoked_result], "search_results": [], "outline": [], "current_idx": 0, "section_drafts": []}


# ------------------------------------------------------------------ #
# Assemble graph
# ------------------------------------------------------------------ #
builder = StateGraph(WorkflowState)

builder.add_node("decide_search", decide_search)
builder.add_node("plan_outline", plan_outline)
builder.add_node("search_section", search_section)
builder.add_node("draft_section", draft_section)
builder.add_node("advance_index", advance_index)
builder.add_node("compile_report", compile_report)
builder.add_node("generate_answer", generate_answer)

# edges
builder.add_edge(START, "decide_search")
builder.add_edge("plan_outline", "search_section")
builder.add_edge("search_section", "draft_section")


# Conditional routing based on `should_search`
def route_after_decision(state: WorkflowState):
    return "plan_outline" if state["should_search"] else "generate_answer"


builder.add_conditional_edges("decide_search", route_after_decision, ["plan_outline", "generate_answer"])

# conditional edge *out of* draft_section
builder.add_conditional_edges(
    "draft_section",
    should_continue,
    {
        "continue": "advance_index",
        "finish": "compile_report",
    },
)

# loop back to search
builder.add_edge("advance_index", "search_section")

# end
builder.add_edge("generate_answer", END)
builder.add_edge("compile_report", END)

graph = builder.compile()

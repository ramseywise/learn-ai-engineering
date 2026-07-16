import json
from datetime import datetime

# LangChain / LangGraph imports
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from src.clients.llm_client import llm
from src.clients.search_client import bing_search

## utilities imports
from src.models.schemas import CustomState
from src.models.search_schemas import BingSearchResult, SearchDecision


###############################################################################
# Graph nodes
###############################################################################
def decide_search(state: CustomState) -> dict:
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
    decision = SearchDecision(**response) if isinstance(response, dict) else response

    return {"should_search": decision.should_search}


def run_search(state: CustomState) -> dict:
    """Executes a Bing search and stores the results with retry logic."""
    # call the llm to formulate a search query for bing
    system_msg = SystemMessage(
        content="You are a search assistant. Formulate a search query for Bing based on the conversation history."
    )
    user_msg = HumanMessage(content=f"Conversation history: {state['messages']}")
    search_query = llm.invoke([system_msg, user_msg])

    # Bing search returns results as JSON string
    results_json = bing_search.invoke(search_query.content)
    results_list = json.loads(results_json.replace("'", '"'))

    if not results_list:  # If no results are found
        return {
            "search_results": [
                BingSearchResult(
                    body="No search results found",
                    href="",
                    title="No Results",
                    index=1,
                )
            ],
        }

    # Normalize the result format to be more understandable for the LLM
    normalized_results: list[BingSearchResult] = []
    for i, item in enumerate(results_list):
        normalized_results.append(
            BingSearchResult(
                body=item.get("snippet", ""),
                href=item.get("link", ""),
                title=item.get("name", ""),  # Bing API uses 'name' for title
                index=i + 1,  # Adding 1-based index for citation purposes
            )
        )

    return {"search_results": normalized_results}


answer_instructions = """
You are a sustainability-focused digital assistant developed. Your primary task is to support in-depth research and answer questions related to sustainability, environmental impact, green technologies, industry practices, and corporate sustainability reports.

If a query is ambiguous or only partially relevant, ask a clarifying question to guide the conversation back to sustainability.
Do not search the internet or generate long replies for unrelated queries. Your focus is always sustainability.

When declining a query, do so professionally and concisely. Keep your tone helpful and respectful. Here are some example behaviors:
- If the user asks "How tall is the Eiffel Tower?" reply with:
    > I'm here to assist with sustainability-related questions. Feel free to ask about environmental topics or industry sustainability practices.

- If the user says "Tell me a joke", respond with:
    > My focus is on providing accurate and helpful sustainability insights. Let me know if you’d like to explore a topic in that area.
        
Today is {today}.

When answering using the search results, cite the claims that require a citation with [href] at the end of the claim.
for example:
"According to the search results, the sky is blue [https://example.com]."

Following search results are available:
{search_results}

"""


def generate_answer(state: CustomState) -> dict:
    results = state.get("search_results", [])

    messages = state["messages"]
    context_block = ""
    if len(results) > 0:
        results_for_json = [result.model_dump() for result in results]
        context_block = f"Search Results:\\n{json.dumps(results_for_json)}"

    now = datetime.now()
    iso_format = now.strftime("%Y-%m-%dT%H:%M:%S")
    system_message = answer_instructions.format(today=iso_format, search_results=context_block)

    # after the search results are added we need to clear them from the state
    invoked_result = llm.invoke([SystemMessage(content=system_message)] + messages)
    return {"messages": [invoked_result], "search_results": []}


###############################################################################
# Graph assembly
###############################################################################

builder = StateGraph(CustomState)

# Nodes
builder.add_node("decide_search", decide_search)
builder.add_node("run_search", run_search)
builder.add_node("generate_answer", generate_answer)

# Edges
builder.add_edge(START, "decide_search")


# Conditional routing based on `should_search`
def route_after_decision(state: CustomState):
    return "run_search" if state["should_search"] else "generate_answer"


builder.add_conditional_edges("decide_search", route_after_decision, ["run_search", "generate_answer"])
# After search → generate answer
builder.add_edge("run_search", "generate_answer")
builder.add_edge("generate_answer", END)

graph = builder.compile()

from langchain_community.tools.bing_search import BingSearchResults
from langchain_community.utilities import BingSearchAPIWrapper

from src.config import (
    _USE_BING,
    BING_SEARCH_URL,
    BING_SUBSCRIPTION_KEY,
)

if _USE_BING:
    bing_search_wrapper = BingSearchAPIWrapper(
        bing_subscription_key=BING_SUBSCRIPTION_KEY, bing_search_url=BING_SEARCH_URL
    )
    bing_search = BingSearchResults(api_wrapper=bing_search_wrapper, num_results=3)

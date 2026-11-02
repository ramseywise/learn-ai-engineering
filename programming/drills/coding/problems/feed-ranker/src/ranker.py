"""You will implement this. See ../prompts.md."""

from typing import List

from store import Post, Store


class FeedRanker:
    def __init__(self, store: Store) -> None:
        self.store = store

    def build_feed(self, user_id: str, limit: int = 20) -> List[Post]:
        raise NotImplementedError

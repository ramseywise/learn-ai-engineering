"""Existing storage layer. You will build on top of this — do not rewrite it."""

from dataclasses import dataclass
from typing import Dict, List, Optional


class ValidationError(Exception):
    """Raised when inbound data fails validation. The API layer maps this to a 400."""


@dataclass(frozen=True)
class Post:
    id: str
    author_id: str
    text: str
    created_at: int          # unix seconds
    likes: int
    reshares: int
    is_deleted: bool = False


@dataclass(frozen=True)
class Follow:
    follower_id: str
    followee_id: str
    muted: bool = False


class Store:
    """In-memory store. Treat as the database — read through these methods only."""

    def __init__(self) -> None:
        self._posts: Dict[str, Post] = {}
        self._follows: List[Follow] = []

    def add_post(self, post: Post) -> None:
        self._posts[post.id] = post

    def add_follow(self, follow: Follow) -> None:
        self._follows.append(follow)

    def get_post(self, post_id: str) -> Optional[Post]:
        return self._posts.get(post_id)

    def posts_by_author(self, author_id: str) -> List[Post]:
        return [p for p in self._posts.values() if p.author_id == author_id]

    def following(self, user_id: str) -> List[Follow]:
        return [f for f in self._follows if f.follower_id == user_id]

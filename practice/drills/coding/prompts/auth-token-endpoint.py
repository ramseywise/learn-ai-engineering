"""Token auth for an API endpoint — practical, 40 min, stdlib only.

PROMPT
    "Implement token-based authentication for an API endpoint. Issue a
    token on login, verify it on protected requests."

Constraint: pure stdlib -- `hmac`, `hashlib`, `secrets`, `base64`, `json`.
No PyJWT, no FastAPI, no bcrypt.

The interviewer answered:
    - Stateless tokens, first-party only, keep it simple.

Clarify the threat model before you design the API. This round is graded on
specific known mistakes rather than on whether the code runs.
"""

import base64
import hashlib
import hmac
import json
import secrets

SECRET = secrets.token_bytes(32)

# user_id -> stored credential material (you decide the shape)
USERS: dict[str, dict] = {}


def register(user_id: str, password: str) -> None:
    raise NotImplementedError


def login(user_id: str, password: str) -> str:
    """Return a signed token, or raise on bad credentials."""
    raise NotImplementedError


def verify_token(token: str) -> dict:
    """Return the token's claims. Raise if the token is not trustworthy."""
    raise NotImplementedError


def protected_endpoint(token: str, required_scopes: set[str] | None = None) -> tuple[int, str]:
    """Return (status_code, body)."""
    raise NotImplementedError


if __name__ == "__main__":
    register("alice", "correct-horse-battery-staple")

    token = login("alice", "correct-horse-battery-staple")
    status, _ = protected_endpoint(token)
    assert status == 200, f"valid token should be accepted, got {status}"

    status, _ = protected_endpoint("garbage.token.here")
    assert status == 401, f"invalid token should be 401, got {status}"

    print("smoke test passed")

    # your edge cases here -- tampered payload, expiry, wrong password, scopes

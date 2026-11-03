"""A strict verifier for HS256 JWTs. Chapter 2. Don't use your own in production."""
import base64
import hashlib
import hmac
import json

class Rejected(Exception):
    """The token isn't acceptable."""

def b64url_decode(text: str) -> bytes:
    """Decode unpadded base64url, the encoding JWTs use."""
    return base64.urlsafe_b64decode(text + '=' * (-len(text) % 4))

def b64url_encode(raw: bytes) -> str:
    """Encode bytes as unpadded base64url."""
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode()

def sign_hs256(key: bytes, signing_input: str) -> str:
    """The HS256 signature of `header.payload`, base64url encoded."""
    raise NotImplementedError()

def verify(token: str, key: bytes, *, iss: str | None, aud: str | None, now: float, typ: str | None='at+jwt') -> dict:
    """Return the claims, or raise Rejected.

    Check the algorithm against HS256 before computing with the key, and compare
    signatures in constant time. Expired means now >= exp. A missing exp is
    rejected. iss, aud or typ set to None skip that one check, for tokens from
    a test vector; a real service always sets them.
    """
    raise NotImplementedError()

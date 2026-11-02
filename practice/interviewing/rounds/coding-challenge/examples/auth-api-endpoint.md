# Worked Example: Auth & API Endpoint (40 min, offline)

> **Constraint note:** pure stdlib — `hmac`, `hashlib`, `secrets`, `base64`, `json`. No PyJWT, no FastAPI, no bcrypt. In production you use the library; the point of writing it by hand once is that you understand what the library is doing when an interviewer asks.

**Format:** 40 min, browser editor.
**Prompt:** *"Implement token-based authentication for an API endpoint. Issue a token on login, verify it on protected requests."*

Auth is the topic where a confident wrong answer is a security incident, so interviewers grade it differently: they are watching for the specific mistakes, and one of them — comparing signatures with `==` — is the single most common failure in this exercise.

---

## 0–5 min — clarify the threat model, not just the API

[NARRATE: "Before I write anything: are we issuing stateless tokens or session ids backed by a store? That's the central tradeoff — stateless scales without a lookup but can't be revoked before expiry; session ids need a store on every request but you can invalidate instantly. And second, is this first-party only, or do third parties get tokens? That changes whether I need scopes."]

Typical answer: stateless, first-party, keep it simple.

[NARRATE: "Then I'll build a signed token — the same structure as a JWT. I'm writing the HMAC by hand since we have no libraries, but I want to say clearly: in production this is PyJWT or Authlib. Hand-rolled crypto is how you get subtle vulnerabilities, and the failure mode is silent — it works perfectly right up until someone attacks it."]

Saying that unprompted is itself a graded signal. Candidates who enjoy writing crypto make interviewers nervous.

---

## 5–15 min — password storage

Even if the prompt is about tokens, they usually want to see login. This is where the first trap sits.

```python
import hashlib
import hmac
import secrets

def hash_password(password: str) -> str:
    """PBKDF2-HMAC-SHA256 with a per-user random salt.

    Stored as `salt$hash`, both hex. Never store the password itself, and never
    a plain SHA-256 of it — fast hashes are the whole problem.
    """
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split("$")
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt_hex), 600_000
    )
    return hmac.compare_digest(candidate.hex(), digest_hex)
```

[NARRATE: "Three things here and each is a real vulnerability if you get it wrong. First, a *slow* hash — PBKDF2 with 600,000 iterations. The instinct is `hashlib.sha256(password)`, but SHA-256 is designed to be fast, and fast is exactly wrong for passwords: a GPU does billions of SHA-256 per second, so a leaked table gets cracked offline. Slow hashing makes each guess expensive. In production I'd prefer bcrypt, scrypt, or Argon2 — PBKDF2 is what's in the stdlib."]

[NARRATE: "Second, a per-user random salt, so two users with the same password get different hashes. Without it, identical hashes reveal identical passwords, and precomputed rainbow tables work. Third, `hmac.compare_digest` rather than `==` — I'll come back to why on the token path, since that's where it really bites."]

---

## 15–28 min — issue and verify the token

```python
import base64
import json
import time

SECRET = secrets.token_bytes(32)          # from env/secrets manager in production
TTL_SECONDS = 900                          # 15 min


def _b64u(raw: bytes) -> bytes:
    """Base64url without padding — the JWT convention."""
    return base64.urlsafe_b64encode(raw).rstrip(b"=")


def _b64u_decode(data: bytes) -> bytes:
    return base64.urlsafe_b64decode(data + b"=" * (-len(data) % 4))


def issue_token(user_id: str, scopes: list[str] | None = None) -> str:
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + TTL_SECONDS,
        "jti": secrets.token_urlsafe(8),   # unique id -> enables revocation lists
        "scopes": scopes or [],
    }
    h = _b64u(json.dumps(header, separators=(",", ":")).encode())
    p = _b64u(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = h + b"." + p
    sig = _b64u(hmac.new(SECRET, signing_input, hashlib.sha256).digest())
    return (signing_input + b"." + sig).decode()
```

[NARRATE: "The payload is signed, not encrypted — anyone holding the token can base64-decode and read it. So no secrets in there: no email, no role names that leak org structure, definitely no PII. It's a claim of identity that the server can verify, not a private envelope."]

Now verification, which is where the exercise is actually graded:

```python
class AuthError(Exception):
    """Raised on any verification failure — never says which one."""


def verify_token(token: str) -> dict:
    parts = token.encode().split(b".")
    if len(parts) != 3:
        raise AuthError("invalid token")
    header_b64, payload_b64, sig = parts

    # 1. Signature FIRST — never parse untrusted claims before verifying them.
    expected = _b64u(hmac.new(SECRET, header_b64 + b"." + payload_b64,
                              hashlib.sha256).digest())
    if not hmac.compare_digest(sig, expected):
        raise AuthError("invalid token")

    # 2. Reject any algorithm we did not choose (the alg=none / alg-confusion attack).
    header = json.loads(_b64u_decode(header_b64))
    if header.get("alg") != "HS256":
        raise AuthError("invalid token")

    # 3. Only now are the claims trustworthy.
    payload = json.loads(_b64u_decode(payload_b64))
    if payload.get("exp", 0) < time.time():
        raise AuthError("invalid token")

    return payload
```

Three narrations, each covering a distinct real-world attack:

[NARRATE: "`hmac.compare_digest`, not `==`. String equality short-circuits on the first differing byte, so the comparison takes measurably longer the more leading bytes are correct. That leaks the signature one byte at a time to anyone who can time requests — it's a timing attack, and it's the classic way a hand-rolled verifier gets broken. `compare_digest` runs in constant time."]

[NARRATE: "I verify the signature *before* parsing the payload. If you decode claims first and check the signature after, you've already made decisions on attacker-controlled data — and people do exactly that, reading `sub` for a log line before verifying."]

[NARRATE: "And I pin the algorithm. The famous JWT vulnerability is a token arriving with `alg` set to `none`, where a naive library sees 'no algorithm' and accepts an unsigned token. The related one is alg-confusion: an attacker sends `HS256` to a server expecting RS256, and the verifier uses the public key as an HMAC secret — which is public. Never trust the token to tell you how to validate it."]

[NARRATE: "Every failure raises the same opaque message. If I said 'expired' versus 'bad signature', I'd be telling an attacker which half of the token to work on. Log the specific reason server-side; return one generic error to the caller."]

---

## 28–36 min — the protected endpoint

```python
from functools import wraps

def require_auth(*required_scopes: str):
    """Decorator enforcing a valid bearer token and, optionally, scopes."""
    def decorator(handler):
        @wraps(handler)
        def wrapper(request, *args, **kwargs):
            header = request.headers.get("Authorization", "")
            scheme, _, raw = header.partition(" ")
            if scheme.lower() != "bearer" or not raw:
                return {"status": 401, "error": "missing or malformed credentials"}
            try:
                claims = verify_token(raw)
            except AuthError:
                return {"status": 401, "error": "invalid credentials"}

            if not set(required_scopes) <= set(claims.get("scopes", [])):
                # 403, not 401 — we know who you are, you just can't do this.
                return {"status": 403, "error": "insufficient scope"}

            request.user = claims["sub"]
            return handler(request, *args, **kwargs)
        return wrapper
    return decorator


@require_auth("reports:read")
def get_report(request, report_id: str):
    return {"status": 200, "report": report_id, "owner": request.user}
```

[NARRATE: "The 401-versus-403 distinction is worth stating: 401 means we don't know who you are, 403 means we do and you're not allowed. Interviewers ask about this and a lot of candidates conflate them."]

[NARRATE: "`functools.wraps` so the handler keeps its name and docstring — without it, framework routing and error messages start reporting every endpoint as 'wrapper'."]

[NARRATE: "One thing this decorator does *not* do, deliberately: authorization on the specific object. Verifying you have `reports:read` isn't the same as verifying this report is yours. That check belongs in the handler with the ownership query, and forgetting it is IDOR — insecure direct object reference — where changing an id in the URL returns someone else's data."]

That last point is the most valuable thing you can say in this exercise, because it's the vulnerability that survives correct authentication.

---

## 36–40 min — close on the tradeoffs you flagged at the start

[NARRATE: "Back to the stateless choice: the cost is that I can't revoke. A stolen token stays valid until it expires, which is why the TTL is 15 minutes rather than a day. The standard fix is a refresh-token pair — short-lived access token, long-lived refresh token that *is* stored server-side and can be revoked. I included a `jti` so a denylist of specific tokens is possible without a full session store."]

[NARRATE: "Next steps: rate-limit the login endpoint, because password hashing at 600K iterations is expensive by design and that makes login a natural DoS target. Rotate the signing secret with a key id in the header so both keys verify during rollover. Enforce HTTPS — a bearer token over plaintext is just a password with extra steps."]

---

## Tests

```python
def test_password_round_trip():
    stored = hash_password("hunter2")
    assert verify_password("hunter2", stored)
    assert not verify_password("hunter3", stored)

def test_salt_is_per_user():
    """Same password, different stored value — no rainbow table, no leak."""
    assert hash_password("hunter2") != hash_password("hunter2")

def test_round_trip():
    assert verify_token(issue_token("u1"))["sub"] == "u1"

def test_tampered_signature_rejected():
    tok = issue_token("u1")
    forged = tok[:-4] + ("aaaa" if not tok.endswith("aaaa") else "bbbb")
    with pytest.raises(AuthError):
        verify_token(forged)

def test_tampered_payload_rejected():
    h, p, s = issue_token("u1").split(".")
    evil = _b64u(json.dumps({"sub": "admin", "exp": 9e9}).encode()).decode()
    with pytest.raises(AuthError):
        verify_token(f"{h}.{evil}.{s}")

def test_alg_none_forgery_rejected():
    """Attacker rewrites the header to alg=none and sends an empty signature."""
    h, p, _ = issue_token("u1").split(".")
    none_h = _b64u(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode()
    with pytest.raises(AuthError):
        verify_token(f"{none_h}.{p}.")

def test_expired_rejected():
    tok = issue_token("u1")
    with mock.patch("time.time", return_value=time.time() + 10_000):
        with pytest.raises(AuthError):
            verify_token(tok)

def test_scope_enforced():
    req = Request({"Authorization": f"Bearer {issue_token('u1', [])}"})
    assert get_report(req, "r1")["status"] == 403          # authenticated, no scope
    ok = Request({"Authorization": f"Bearer {issue_token('u1', ['reports:read'])}"})
    assert get_report(ok, "r1")["status"] == 200

@pytest.mark.parametrize("header", [None, "Basic abc", "Bearer garbage"])
def test_missing_or_bad_credentials(header):
    req = Request({"Authorization": header} if header else {})
    assert get_report(req, "r1")["status"] == 401
```

[NARRATE: "The payload-tampering test is the important one — it's the actual attack. Someone takes their own valid token, swaps `sub` to `admin`, and replays it. That must fail on the signature check."]

---

## What the interviewer is grading

| Signal | Where it appeared |
|---|---|
| Threat model before code | Asked stateless-vs-session, named the revocation tradeoff |
| Knows not to roll crypto | Said "PyJWT in production" unprompted |
| Slow password hash | PBKDF2 + high iterations, and *why* fast hashes lose |
| Per-user salt | Named rainbow tables and identical-hash leakage |
| **Constant-time compare** | `hmac.compare_digest`, with the timing-attack explanation |
| Verify before parse | Signature checked before any claim is read |
| Algorithm pinning | `alg=none` and alg-confusion named explicitly |
| Opaque errors | One message for every failure path |
| 401 vs 403 | Distinguished correctly |
| Knows what auth *doesn't* cover | IDOR — object-level ownership is a separate check |

The weakest version stores `sha256(password)` with no salt, compares signatures with `==`, decodes the payload before verifying it, and returns "token expired" so an attacker knows the signature was fine.

---

## The five things to have cold

If you remember nothing else from this file:

1. **`hmac.compare_digest`, never `==`** — timing attack.
2. **Slow hash + per-user salt** for passwords — never plain SHA-256.
3. **Verify the signature before parsing claims**, and **pin the algorithm**.
4. **401 = who are you; 403 = not allowed.**
5. **Authentication ≠ authorization** — object ownership is a separate check (IDOR).

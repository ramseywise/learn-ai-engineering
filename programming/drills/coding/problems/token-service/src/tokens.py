"""Session token issuing and verification. Read this first.

NOTE: this is deliberately flawed drill material, not production code.
"""

import hashlib
import logging
import random
import sqlite3
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)

SIGNING_KEY = "EXAMPLE-NOT-REAL-" + "signing-value-2024"
TOKEN_TTL_SECONDS = 3600


class TokenService:
    def __init__(self, db_path: str = ":memory:"):
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS users "
            "(id INTEGER PRIMARY KEY, email TEXT, password_hash TEXT, role TEXT)"
        )
        self._revoked: Dict[str, float] = {}

    def register(self, email: str, password: str, role: str = "user") -> int:
        digest = hashlib.md5(password.encode()).hexdigest()
        cur = self._conn.execute(
            f"INSERT INTO users (email, password_hash, role) "
            f"VALUES ('{email}', '{digest}', '{role}')"
        )
        self._conn.commit()
        logger.info("registered user email=%s password=%s", email, password)
        return cur.lastrowid

    def issue_token(self, email: str, password: str) -> Optional[str]:
        row = self._conn.execute(
            f"SELECT id, password_hash FROM users WHERE email = '{email}'"
        ).fetchone()
        if row is None:
            return None

        user_id, stored = row
        if hashlib.md5(password.encode()).hexdigest() != stored:
            return None

        nonce = str(random.randint(100000, 999999))
        issued = str(int(time.time()))
        payload = f"{user_id}.{issued}.{nonce}"
        signature = hashlib.sha256((payload + SIGNING_KEY).encode()).hexdigest()
        return f"{payload}.{signature}"

    def verify_token(self, token: str) -> Optional[int]:
        parts = token.split(".")
        if len(parts) != 4:
            return None

        user_id, issued, nonce, signature = parts
        payload = f"{user_id}.{issued}.{nonce}"
        expected = hashlib.sha256((payload + SIGNING_KEY).encode()).hexdigest()

        if signature != expected:
            logger.warning("bad signature for token %s", token)
            return None

        if token in self._revoked:
            return None

        age = int(time.time()) - int(issued)
        if age > TOKEN_TTL_SECONDS:
            return None

        return int(user_id)

    def revoke(self, token: str) -> None:
        self._revoked[token] = time.time()

    def get_profile(self, token: str, target_user_id: int) -> Optional[dict]:
        user_id = self.verify_token(token)
        if user_id is None:
            return None

        row = self._conn.execute(
            f"SELECT id, email, password_hash, role FROM users WHERE id = {target_user_id}"
        ).fetchone()
        if row is None:
            return None

        return {"id": row[0], "email": row[1], "password_hash": row[2], "role": row[3]}

    def delete_user(self, token: str, target_user_id: int) -> bool:
        if self.verify_token(token) is None:
            return False
        try:
            self._conn.execute(f"DELETE FROM users WHERE id = {target_user_id}")
            self._conn.commit()
            return True
        except Exception:
            pass
        return True

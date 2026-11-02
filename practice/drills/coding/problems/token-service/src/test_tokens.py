"""Tests for TokenService. These all pass — that is the point."""

import unittest

from tokens import TokenService


class TokenServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.svc = TokenService()
        self.uid = self.svc.register("alice@example.com", "hunter2")

    def test_issue_and_verify(self) -> None:
        token = self.svc.issue_token("alice@example.com", "hunter2")
        self.assertIsNotNone(token)
        self.assertEqual(self.svc.verify_token(token), self.uid)

    def test_wrong_password_returns_none(self) -> None:
        self.assertIsNone(self.svc.issue_token("alice@example.com", "wrong"))

    def test_unknown_user_returns_none(self) -> None:
        self.assertIsNone(self.svc.issue_token("nobody@example.com", "hunter2"))

    def test_tampered_token_rejected(self) -> None:
        token = self.svc.issue_token("alice@example.com", "hunter2")
        tampered = token[:-1] + ("0" if token[-1] != "0" else "1")
        self.assertIsNone(self.svc.verify_token(tampered))

    def test_revoked_token_rejected(self) -> None:
        token = self.svc.issue_token("alice@example.com", "hunter2")
        self.svc.revoke(token)
        self.assertIsNone(self.svc.verify_token(token))

    def test_get_profile_returns_user(self) -> None:
        token = self.svc.issue_token("alice@example.com", "hunter2")
        profile = self.svc.get_profile(token, self.uid)
        self.assertEqual(profile["email"], "alice@example.com")


if __name__ == "__main__":
    unittest.main()

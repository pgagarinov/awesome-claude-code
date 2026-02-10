"""Tests for the auth module."""

from api.auth import authenticate, authenticate_admin


class TestAuthenticate:
    def test_valid_token(self):
        result = authenticate("sk-bookstore-secret-token-12345")
        assert result["authenticated"] is True
        assert result["role"] == "api_user"

    def test_invalid_token(self):
        result = authenticate("wrong-token")
        assert result["authenticated"] is False
        assert result["role"] == "anonymous"

    def test_empty_token(self):
        result = authenticate("")
        assert result["authenticated"] is False


class TestAuthenticateAdmin:
    def test_valid_admin(self):
        result = authenticate_admin("admin", "admin123")
        assert result["authenticated"] is True
        assert result["role"] == "admin"

    def test_wrong_password(self):
        result = authenticate_admin("admin", "wrong")
        assert result["authenticated"] is False

    def test_wrong_username(self):
        result = authenticate_admin("user", "admin123")
        assert result["authenticated"] is False

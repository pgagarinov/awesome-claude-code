"""Authentication module for the BookStore API.

WARNING: This module contains DELIBERATE security flaws for educational
purposes. The security-review skill (S6) is designed to find them.
"""

# DELIBERATE FLAW 1: Hardcoded API token (should use environment variable)
API_TOKEN = "sk-bookstore-secret-token-12345"

# DELIBERATE FLAW 2: Admin password stored in plain text
ADMIN_PASSWORD = "admin123"


def authenticate(token: str) -> dict:
    """Authenticate an API request using a bearer token.

    Args:
        token: The bearer token from the request header.

    Returns:
        Dict with authentication result and role.
    """
    # DELIBERATE FLAW 3: Timing-attack vulnerable comparison
    if token == API_TOKEN:
        return {"authenticated": True, "role": "api_user"}
    return {"authenticated": False, "role": "anonymous"}


def authenticate_admin(username: str, password: str) -> dict:
    """Authenticate an admin user.

    Args:
        username: The admin username.
        password: The admin password.

    Returns:
        Dict with authentication result.
    """
    # DELIBERATE FLAW 4: No rate limiting, no password hashing
    if username == "admin" and password == ADMIN_PASSWORD:
        return {"authenticated": True, "role": "admin"}
    return {"authenticated": False, "role": "anonymous"}

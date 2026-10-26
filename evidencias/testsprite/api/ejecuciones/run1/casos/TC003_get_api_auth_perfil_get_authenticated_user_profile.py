import requests
import sys
from requests.exceptions import RequestException

BASE_URL = "http://localhost:3000"
TOKEN = "<ADMIN_JWT_REDACTED>"

def test_get_authenticated_user_profile():
    url = f"{BASE_URL}/api/auth/perfil"
    headers = {
        "x-token": TOKEN,
        "Accept": "application/json"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
    except RequestException as e:
        raise AssertionError(f"Request to {url} failed: {e}") from e

    # Basic status code check
    if resp.status_code != 200:
        # Try to include error body for debugging
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        raise AssertionError(f"Expected status 200 but got {resp.status_code}. Response: {err}")

    # Content-Type should be JSON
    ct = resp.headers.get("Content-Type", "")
    assert "application/json" in ct or ct.startswith("application/json"), f"Expected JSON response, got Content-Type: {ct}"

    try:
        body = resp.json()
    except ValueError as e:
        raise AssertionError(f"Response body is not valid JSON: {e}") from e

    # The API may return the user directly or wrapped in a 'usuario' field
    if isinstance(body, dict) and "usuario" in body:
        user = body["usuario"]
    else:
        user = body

    assert isinstance(user, dict), f"Expected user object (dict), got: {type(user)}"

    # Validate presence of key profile fields according to PRD: 'nombre' and 'email' should exist
    assert "nombre" in user, f"'nombre' not found in user profile: {user.keys()}"
    assert "email" in user, f"'email' not found in user profile: {user.keys()}"

    # Password should not be exposed
    assert "password" not in user, "Password must not be present in the profile response"

    # Optionally check role if present
    if "rol" in user:
        assert user["rol"] in ("admin", "usuario"), f"Unexpected rol value: {user['rol']}"

    print("TC003 passed: Authenticated user profile retrieved successfully.")

if __name__ == "__main__":
    try:
        test_get_authenticated_user_profile()
    except AssertionError as e:
        print(f"TC003 failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC003 encountered an unexpected error: {e}")
        sys.exit(2)
    sys.exit(0)
import requests
import sys

BASE_URL = "http://localhost:3000"
TOKEN = "<ADMIN_JWT_REDACTED>"
TIMEOUT = 30


def test_get_authenticated_user_profile():
    url = f"{BASE_URL}/api/auth/perfil"
    headers = {
        "x-token": TOKEN,
        "Accept": "application/json"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"Request to {url} failed: {e}")

    # Assert status code
    if resp.status_code != 200:
        # try to include response body for debugging
        body = None
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        raise AssertionError(f"Expected status 200 but got {resp.status_code}. Response body: {body}")

    # Assert content-type is JSON (best-effort)
    content_type = resp.headers.get("Content-Type", "")
    if "application/json" not in content_type.lower():
        raise AssertionError(f"Expected JSON response but Content-Type was: {content_type}")

    # Parse JSON
    try:
        data = resp.json()
    except ValueError as e:
        raise AssertionError(f"Response returned invalid JSON: {e}")

    if not isinstance(data, dict):
        raise AssertionError(f"Expected JSON object for user profile, got: {type(data)}")

    # Validate required user fields
    required_fields = ["email", "rol", "nombre"]
    for field in required_fields:
        assert field in data, f"Expected field '{field}' in profile response"

    # Password should not be present in profile response
    assert "password" not in data, "Password should not be included in the profile response"

    # Token provided is an admin token; expect rol 'admin'
    assert data.get("rol") == "admin", f"Expected role 'admin' for the token used, got: {data.get('rol')}"

    print("test_get_authenticated_user_profile: PASSED")


if __name__ == "__main__":
    try:
        test_get_authenticated_user_profile()
    except AssertionError as e:
        print(f"test_get_authenticated_user_profile: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"test_get_authenticated_user_profile: ERROR - {e}")
        sys.exit(2)
    sys.exit(0)
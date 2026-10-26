import requests
import sys

BASE_URL = "http://localhost:3000"
TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "x-token": TOKEN,
    "Accept": "application/json"
}
TIMEOUT = 30


def test_get_authenticated_user_profile():
    url = f"{BASE_URL}/api/auth/perfil"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"Request to {url} failed: {e}")

    # Assert status code
    assert resp.status_code == 200, f"Expected status 200, got {resp.status_code}. Response body: {resp.text}"

    # Assert content-type looks like JSON
    content_type = resp.headers.get("Content-Type", "")
    assert "application/json" in content_type or "json" in content_type, f"Expected JSON response, got Content-Type: {content_type}"

    # Parse JSON
    try:
        data = resp.json()
    except ValueError:
        raise AssertionError(f"Response is not valid JSON. Raw response: {resp.text}")

    # The profile should be an object (dict)
    assert isinstance(data, dict), f"Expected JSON object for user profile, got {type(data)}"

    # Required fields checks
    assert "email" in data and isinstance(data["email"], str) and data["email"], "User profile missing valid 'email'"
    assert "nombre" in data and isinstance(data["nombre"], str) and data["nombre"], "User profile missing valid 'nombre'"

    # Ensure password is not leaked
    assert "password" not in data, "Response contains 'password' field which must not be present"

    # Ensure there's some form of identifier
    id_keys = ("_id", "id", "uid")
    assert any(k in data for k in id_keys), f"User profile missing an identifier; expected one of {id_keys}, got keys: {list(data.keys())}"

    # Optional: role and estado if present should have expected types
    if "rol" in data:
        assert isinstance(data["rol"], str) and data["rol"], "If present, 'rol' must be a non-empty string"
    if "estado" in data:
        assert isinstance(data["estado"], bool), "'estado' if present must be a boolean"

    return True


if __name__ == "__main__":
    # First execution
    try:
        test_get_authenticated_user_profile()
        print("First run: PASS")
    except AssertionError as e:
        print(f"First run: FAIL - {e}")
        sys.exit(1)

    # Second execution to confirm stability
    try:
        test_get_authenticated_user_profile()
        print("Second run: PASS")
    except AssertionError as e:
        print(f"Second run: FAIL - {e}")
        sys.exit(1)

    print("TC003 completed successfully.")
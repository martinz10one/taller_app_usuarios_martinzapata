import requests
import uuid
import sys
import time

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "Content-Type": "application/json",
    "x-token": ADMIN_TOKEN
}
TIMEOUT = 30


def test_get_api_usuarios_id_get_user_details_by_id_TC007():
    created_user = None
    user_id = None

    # Create a new user to test retrieval (admin endpoint)
    unique_email = f"test_tc007_{uuid.uuid4().hex[:8]}@example.com"
    create_payload = {
        "nombre": "Test User TC007",
        "email": unique_email,
        "password": "Password123",
        "rol": "usuario"
    }

    try:
        resp = requests.post(
            f"{BASE_URL}/api/usuarios",
            json=create_payload,
            headers=HEADERS,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        raise AssertionError(f"Request to create user failed: {e}")

    assert resp.status_code == 201, f"Expected 201 when creating user, got {resp.status_code}, body: {resp.text}"

    try:
        created_json = resp.json()
    except ValueError:
        raise AssertionError(f"Create user response is not valid JSON: {resp.text}")

    # Extract user object and id (support different response shapes)
    if isinstance(created_json, dict) and "usuario" in created_json and isinstance(created_json["usuario"], dict):
        created_user = created_json["usuario"]
    elif isinstance(created_json, dict) and ("nombre" in created_json and "email" in created_json and any(k in created_json for k in ("_id", "id", "uid"))):
        created_user = created_json
    else:
        # fallback: if API returns nested or other shape, try to find keys
        # Search for first dict with 'email' matching
        if isinstance(created_json, dict):
            found = None
            for v in created_json.values():
                if isinstance(v, dict) and v.get("email") == unique_email:
                    found = v
                    break
            if found:
                created_user = found

    assert created_user is not None, f"Could not locate created user in response: {created_json}"
    user_id = created_user.get("_id") or created_user.get("id") or created_user.get("uid")
    assert user_id, f"Created user does not contain an id: {created_user}"

    # Wait a short moment to ensure DB consistency (helpful for second stability GET)
    time.sleep(0.5)

    # Perform the GET request twice to confirm stability after the first run passed
    get_url = f"{BASE_URL}/api/usuarios/{user_id}"
    retrieved = None
    for attempt in (1, 2):
        try:
            get_resp = requests.get(get_url, headers=HEADERS, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Request to get user (attempt {attempt}) failed: {e}")

        assert get_resp.status_code == 200, f"Attempt {attempt}: Expected 200 when retrieving user, got {get_resp.status_code}, body: {get_resp.text}"

        try:
            get_json = get_resp.json()
        except ValueError:
            raise AssertionError(f"Attempt {attempt}: Get user response is not valid JSON: {get_resp.text}")

        # The GET may return the user object directly or under 'usuario'
        if isinstance(get_json, dict) and "usuario" in get_json and isinstance(get_json["usuario"], dict):
            retrieved = get_json["usuario"]
        elif isinstance(get_json, dict) and ("nombre" in get_json and "email" in get_json and any(k in get_json for k in ("_id", "id", "uid"))):
            retrieved = get_json
        else:
            # Try to find user-like dict inside response
            found = None
            if isinstance(get_json, dict):
                for v in get_json.values():
                    if isinstance(v, dict) and (v.get("_id") == user_id or v.get("id") == user_id or v.get("uid") == user_id or v.get("email") == unique_email):
                        found = v
                        break
            if found:
                retrieved = found

        assert retrieved is not None, f"Attempt {attempt}: Could not parse user details from response: {get_json}"

        # Basic validations against created data
        retrieved_id = retrieved.get("_id") or retrieved.get("id") or retrieved.get("uid")
        assert retrieved_id == user_id, f"Attempt {attempt}: Retrieved id does not match created id"
        assert retrieved.get("email") == unique_email, f"Attempt {attempt}: Retrieved email does not match created email"
        assert retrieved.get("nombre") == create_payload["nombre"], f"Attempt {attempt}: Retrieved nombre does not match created nombre"

    # If we reach here, both GET attempts succeeded and matched created data
    # Cleanup: delete the created user (logical delete)
    try:
        del_resp = requests.delete(f"{BASE_URL}/api/usuarios/{user_id}", headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request to delete user failed: {e}")

    # Accept 200 for successful logical delete, or 404 if already not found (tolerate but fail if unexpected)
    if del_resp.status_code not in (200, 404):
        raise AssertionError(f"Unexpected status code when deleting user: {del_resp.status_code}, body: {del_resp.text}")

    print("TC007 passed: Admin retrieved user details by id successfully (verified twice).")


if __name__ == "__main__":
    try:
        test_get_api_usuarios_id_get_user_details_by_id_TC007()
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        sys.exit(2)
    else:
        print("TEST SUCCESS")
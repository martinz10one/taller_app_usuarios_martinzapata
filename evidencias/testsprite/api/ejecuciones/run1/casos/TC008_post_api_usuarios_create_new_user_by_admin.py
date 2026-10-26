import requests
import uuid
import re
import sys

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
TIMEOUT = 30

def test_tc008_post_api_usuarios_create_new_user_by_admin():
    headers = {
        "Content-Type": "application/json",
        "x-token": ADMIN_TOKEN
    }

    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    plain_password = "Password1A"  # meets typical policy: min 8, upper, lower, number
    payload = {
        "nombre": "Test User",
        "email": unique_email,
        "password": plain_password,
        "rol": "usuario"
    }

    created_user_id = None

    try:
        # Create user as admin
        try:
            resp = requests.post(f"{BASE_URL}/api/usuarios", json=payload, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Request to create user failed: {e}")

        assert resp is not None, "No response received when creating user"
        assert resp.status_code == 201, f"Expected 201 Created, got {resp.status_code}: {resp.text}"

        try:
            user_obj = resp.json()
        except ValueError:
            raise AssertionError(f"Response is not valid JSON: {resp.text}")

        assert isinstance(user_obj, dict), f"Expected JSON object for created user, got: {type(user_obj)}"

        # Determine user id property
        if "uid" in user_obj:
            created_user_id = user_obj["uid"]
        elif "id" in user_obj:
            created_user_id = user_obj["id"]
        elif "_id" in user_obj:
            created_user_id = user_obj["_id"]
        else:
            # Try nested 'usuario' key (some APIs return { usuario: { ... } })
            if "usuario" in user_obj and isinstance(user_obj["usuario"], dict):
                nested = user_obj["usuario"]
                if "uid" in nested:
                    created_user_id = nested["uid"]
                elif "id" in nested:
                    created_user_id = nested["id"]
                elif "_id" in nested:
                    created_user_id = nested["_id"]
                else:
                    # if still no id, attempt to find any plausible id field
                    for k in ("_id", "id", "uid"):
                        if k in nested:
                            created_user_id = nested[k]
                            break
                user_obj = nested  # treat nested as the user object
            else:
                raise AssertionError(f"Created user object does not contain an id. Response: {user_obj}")

        # Basic checks on returned user fields
        assert user_obj.get("email") == unique_email, f"Returned user email mismatch: expected {unique_email}, got {user_obj.get('email')}"
        assert user_obj.get("nombre") == "Test User", f"Returned user nombre mismatch: expected 'Test User', got {user_obj.get('nombre')}"
        assert user_obj.get("rol") in ("usuario", "admin"), f"Returned user rol unexpected: {user_obj.get('rol')}"

        # Verify password handling: if password field is returned, it must be hashed (not equal to plain) and look like bcrypt
        if "password" in user_obj:
            returned_password = user_obj["password"]
            assert returned_password != plain_password, "Returned password matches plaintext; it should be hashed or not returned"
            # common bcrypt hash prefix $2a$, $2b$, $2y$
            assert re.match(r"^\$2[aby]\$[0-9]{2}\$.{53}$", returned_password) or returned_password.startswith("$2"), \
                f"Returned password does not match expected bcrypt pattern: {returned_password}"
        else:
            # If password is not returned (preferred), verify credentials by logging in with the created user
            login_payload = {"email": unique_email, "password": plain_password}
            try:
                login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload, timeout=TIMEOUT)
            except requests.RequestException as e:
                raise AssertionError(f"Login request failed for created user: {e}")
            assert login_resp.status_code == 200, f"Login with created user failed, expected 200, got {login_resp.status_code}: {login_resp.text}"
            try:
                login_json = login_resp.json()
            except ValueError:
                raise AssertionError(f"Login response not JSON: {login_resp.text}")
            assert "token" in login_json and "usuario" in login_json, f"Login response missing token/usuario: {login_json}"

    finally:
        # Cleanup: delete created user if we have its id
        if created_user_id:
            try:
                del_resp = requests.delete(f"{BASE_URL}/api/usuarios/{created_user_id}", headers=headers, timeout=TIMEOUT)
            except requests.RequestException as e:
                # Can't raise in finally; print and exit non-zero
                print(f"Warning: failed to delete test user {created_user_id}: {e}", file=sys.stderr)
                raise
            # Acceptable deletion responses: 200 OK; if already deleted or not found, could be 404 but we assert 200 as expected
            assert del_resp.status_code == 200, f"Expected 200 on delete, got {del_resp.status_code}: {del_resp.text}"

if __name__ == "__main__":
    test_tc008_post_api_usuarios_create_new_user_by_admin()
    print("TC008 passed")
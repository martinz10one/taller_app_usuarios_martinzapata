import requests
import uuid
import time
import random
import string
import sys

BASE_URL = "http://localhost:3000"
TIMEOUT = 30
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS_JSON = {"Content-Type": "application/json"}


def _extract_user_id(usuario_obj):
    # Try common id fields
    for key in ("_id", "uid", "id"):
        if isinstance(usuario_obj, dict) and key in usuario_obj:
            return usuario_obj[key]
    return None


def _random_email():
    timestamp = int(time.time() * 1000)
    rnd = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"testuser_{timestamp}_{rnd}@example.com"


def test_post_api_auth_login_authenticate_user():
    """
    TC002: Verify that a user can log in with valid email and password,
    receiving a 200 status with a token and usuario object.
    This test will:
      - create a new user via POST /api/auth/registro
      - perform POST /api/auth/login twice to confirm stability
      - validate responses
      - delete the created user using admin DELETE /api/usuarios/:id in finally
    """
    created_user_id = None
    email = _random_email()
    password = "Aa12345678"  # meets policy: uppercase, lowercase, number, length >=8
    nombre = "Test User"

    try:
        # 1) Create user (registration)
        reg_url = f"{BASE_URL}/api/auth/registro"
        reg_payload = {"nombre": nombre, "email": email, "password": password}
        try:
            reg_resp = requests.post(reg_url, json=reg_payload, headers=HEADERS_JSON, timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise AssertionError(f"Registration request failed: {e}")

        if reg_resp.status_code != 201:
            raise AssertionError(f"Expected 201 from registration, got {reg_resp.status_code}: {reg_resp.text}")

        try:
            reg_json = reg_resp.json()
        except ValueError:
            raise AssertionError(f"Registration response is not valid JSON: {reg_resp.text}")

        # Expect token and usuario in registration response
        assert "token" in reg_json and isinstance(reg_json["token"], str) and reg_json["token"].strip() != "", \
            f"Registration response missing token: {reg_json}"
        assert "usuario" in reg_json and isinstance(reg_json["usuario"], dict), \
            f"Registration response missing usuario object: {reg_json}"

        created_user_id = _extract_user_id(reg_json["usuario"])
        assert created_user_id is not None, f"Could not determine created user id from usuario: {reg_json['usuario']}"

        # 2) Perform login twice to confirm stability
        login_url = f"{BASE_URL}/api/auth/login"
        login_payload = {"email": email, "password": password}

        for attempt in (1, 2):
            try:
                login_resp = requests.post(login_url, json=login_payload, headers=HEADERS_JSON, timeout=TIMEOUT)
            except requests.exceptions.RequestException as e:
                raise AssertionError(f"Login request attempt {attempt} failed: {e}")

            if login_resp.status_code != 200:
                raise AssertionError(f"Expected 200 from login (attempt {attempt}), got {login_resp.status_code}: {login_resp.text}")

            try:
                login_json = login_resp.json()
            except ValueError:
                raise AssertionError(f"Login response (attempt {attempt}) is not valid JSON: {login_resp.text}")

            # Validate presence of token and usuario
            assert "token" in login_json and isinstance(login_json["token"], str) and login_json["token"].strip() != "", \
                f"Login response (attempt {attempt}) missing token: {login_json}"
            assert "usuario" in login_json and isinstance(login_json["usuario"], dict), \
                f"Login response (attempt {attempt}) missing usuario object: {login_json}"

            usuario = login_json["usuario"]
            # usuario should not include password field in response
            assert "password" not in usuario, f"Login response (attempt {attempt}) usuario should not contain password: {usuario}"
            # email should match
            assert usuario.get("email") == email, f"Login response (attempt {attempt}) usuario.email mismatch: expected {email}, got {usuario.get('email')}"

    finally:
        # Cleanup: delete created user if exists
        if created_user_id:
            delete_url = f"{BASE_URL}/api/usuarios/{created_user_id}"
            headers = {"x-token": ADMIN_TOKEN, "Content-Type": "application/json"}
            try:
                del_resp = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
            except requests.exceptions.RequestException as e:
                # If deletion fails at HTTP level, raise to surface cleanup issue
                raise AssertionError(f"Failed to send delete request for cleanup: {e}")

            if del_resp.status_code not in (200, 404):
                # 404 could mean already removed; treat as ok. Anything else is unexpected.
                raise AssertionError(f"Unexpected status deleting user {created_user_id}: {del_resp.status_code}: {del_resp.text}")


if __name__ == "__main__":
    try:
        test_post_api_auth_login_authenticate_user()
        print("TC002 passed")
    except AssertionError as e:
        print(f"TC002 failed: {e}")
        sys.exit(1)
    except Exception as ex:
        print(f"TC002 encountered an unexpected error: {ex}")
        sys.exit(2)
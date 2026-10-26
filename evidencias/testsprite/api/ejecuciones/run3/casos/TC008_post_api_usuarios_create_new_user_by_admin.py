import requests
import time
import uuid
import sys

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "x-token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}
TIMEOUT = 30


def test_TC008_post_api_usuarios_create_new_user_by_admin():
    # Prepare unique user data
    unique_suffix = str(int(time.time() * 1000)) + uuid.uuid4().hex[:6]
    nombre = f"Test User {unique_suffix}"
    email = f"testuser_{unique_suffix}@example.com"
    password = "Password123"  # meets complexity: uppercase, lowercase, number
    rol = "usuario"  # admin creates a regular user

    create_payload = {
        "nombre": nombre,
        "email": email,
        "password": password,
        "rol": rol
    }

    created_user_id = None

    try:
        # Create user as admin
        resp = requests.post(f"{BASE_URL}/api/usuarios", json=create_payload, headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request to create user failed: {e}")

    # Validate creation response
    try:
        assert resp.status_code == 201, f"Expected 201 Created, got {resp.status_code}, body: {resp.text}"
        resp_json = resp.json()
    except ValueError:
        raise AssertionError(f"Response is not valid JSON. Status: {resp.status_code}, Body: {resp.text}")

    # Extract user object (API may return the user directly or under 'usuario')
    if isinstance(resp_json, dict) and "usuario" in resp_json:
        user = resp_json["usuario"]
    else:
        user = resp_json

    assert isinstance(user, dict), f"Created user is not a JSON object: {user}"

    # Basic field validations
    assert user.get("email") == email, f"Returned email mismatch. Expected {email}, got {user.get('email')}"
    assert user.get("nombre") == nombre, f"Returned nombre mismatch. Expected {nombre}, got {user.get('nombre')}"
    # Role should be set to 'usuario' as provided
    assert user.get("rol") == rol, f"Returned rol mismatch. Expected {rol}, got {user.get('rol')}"

    # Ensure password is not returned in plain text. If password field exists, it must not equal the plaintext.
    if "password" in user:
        assert user["password"] != password, "API returned plaintext password equal to submitted password"

    # Extract ID (support common id fields)
    created_user_id = user.get("_id") or user.get("id") or user.get("uid")
    assert created_user_id, f"Created user id not found in response: {user}"

    # Verify that the stored password allows login (implies it was hashed and stored correctly)
    login_payload = {"email": email, "password": password}
    try:
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request to login as created user failed: {e}")

    try:
        assert login_resp.status_code == 200, f"Expected 200 OK on login, got {login_resp.status_code}, body: {login_resp.text}"
        login_json = login_resp.json()
    except ValueError:
        raise AssertionError(f"Login response is not valid JSON. Status: {login_resp.status_code}, Body: {login_resp.text}")

    # Ensure login response contains token and usuario info
    assert isinstance(login_json, dict), f"Login response unexpected format: {login_json}"
    token_present = bool(login_json.get("token"))
    usuario_present = bool(login_json.get("usuario")) or ("email" in login_json and login_json.get("email") == email)
    assert token_present or usuario_present, f"Login response missing token/usuario: {login_json}"

    # If usuario provided, check email matches
    if login_json.get("usuario"):
        logged_user = login_json["usuario"]
        assert logged_user.get("email") == email, f"Login returned usuario with unexpected email: {logged_user.get('email')}"

    # Cleanup: delete the created user (logical delete) using admin token
    try:
        del_resp = requests.delete(f"{BASE_URL}/api/usuarios/{created_user_id}", headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request to delete created user failed: {e}")

    # Expect 200 OK on deletion
    try:
        assert del_resp.status_code == 200, f"Expected 200 on delete, got {del_resp.status_code}, body: {del_resp.text}"
    except AssertionError:
        # If delete failed, surface the response for debugging
        raise


if __name__ == "__main__":
    test_TC008_post_api_usuarios_create_new_user_by_admin()
    print("TC008 passed.")
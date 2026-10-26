import requests
import uuid
import sys

BASE_URL = "http://localhost:3000"
TIMEOUT = 30
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"


def test_put_api_auth_password_change_user_password():
    user_id = None
    user_token = None

    # Prepare unique user credentials
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"testuser_{unique_suffix}@example.com"
    nombre = "Test User"
    password_actual = "Passw0rdA1!"
    password_nueva = "NewPassw0rdB2!"

    try:
        # 1) Register a new user
        registro_url = f"{BASE_URL}/api/auth/registro"
        registro_payload = {
            "nombre": nombre,
            "email": email,
            "password": password_actual
        }
        resp = requests.post(registro_url, json=registro_payload, timeout=TIMEOUT)
        try:
            resp_json = resp.json()
        except ValueError:
            resp_json = None

        assert resp.status_code == 201, f"Expected 201 on registration, got {resp.status_code}, body: {resp.text}"
        assert resp_json and "token" in resp_json, f"Registration response missing token: {resp_json}"
        assert resp_json and "usuario" in resp_json, f"Registration response missing usuario: {resp_json}"

        user_token = resp_json["token"]
        usuario = resp_json["usuario"]
        # the API may use uid or _id
        user_id = usuario.get("uid") or usuario.get("_id") or usuario.get("id")
        assert user_id, f"Could not determine created user id from usuario: {usuario}"

        # 2) Change password using PUT /api/auth/password with the user's token
        change_pw_url = f"{BASE_URL}/api/auth/password"
        headers_user = {"x-token": user_token, "Content-Type": "application/json"}
        change_payload = {
            "passwordActual": password_actual,
            "passwordNueva": password_nueva
        }
        resp = requests.put(change_pw_url, json=change_payload, headers=headers_user, timeout=TIMEOUT)
        try:
            resp_json = resp.json()
        except ValueError:
            resp_json = None

        assert resp.status_code == 200, f"Expected 200 on password change, got {resp.status_code}, body: {resp.text}"
        assert resp_json and resp_json.get("mensaje") == "Contraseña actualizada", f"Unexpected password change response: {resp_json}"

        # 3) Verify login with new password succeeds
        login_url = f"{BASE_URL}/api/auth/login"
        login_payload_new = {"email": email, "password": password_nueva}
        resp = requests.post(login_url, json=login_payload_new, timeout=TIMEOUT)
        try:
            resp_json = resp.json()
        except ValueError:
            resp_json = None

        assert resp.status_code == 200, f"Expected 200 on login with new password, got {resp.status_code}, body: {resp.text}"
        assert resp_json and "token" in resp_json and "usuario" in resp_json, f"Login (new password) response missing expected fields: {resp_json}"

        # 4) Verify login with old password fails (should be 401)
        login_payload_old = {"email": email, "password": password_actual}
        resp = requests.post(login_url, json=login_payload_old, timeout=TIMEOUT)
        # Accept either 401 or 400 depending on implementation, but not 200
        assert resp.status_code != 200, f"Login with old password unexpectedly succeeded, body: {resp.text}"
    except requests.RequestException as e:
        raise AssertionError(f"HTTP request failed: {e}")
    finally:
        # Cleanup: delete the created user using admin token if we have an id
        if user_id:
            try:
                delete_url = f"{BASE_URL}/api/usuarios/{user_id}"
                headers_admin = {"x-token": ADMIN_TOKEN}
                resp = requests.delete(delete_url, headers=headers_admin, timeout=TIMEOUT)
                # Accept 200 as successful deletion; if 404 or 400, print for visibility but do not fail cleanup
                if resp.status_code not in (200,):
                    # Try to surface a helpful message if deletion didn't return 200
                    try:
                        body = resp.json()
                    except ValueError:
                        body = resp.text
                    print(f"Cleanup: unexpected status deleting user {user_id}: {resp.status_code}, body: {body}", file=sys.stderr)
            except requests.RequestException as e:
                print(f"Cleanup: failed to delete user {user_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    test_put_api_auth_password_change_user_password()
    print("Test TC005 completed successfully.")
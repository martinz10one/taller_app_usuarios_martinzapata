import requests
import time
import random
import string
import sys

BASE_URL = "http://localhost:3000"
TIMEOUT = 30
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"


def test_post_api_auth_login_authenticate_user():
    # Create unique user
    unique_email = f"testuser_{int(time.time())}_{random.randint(1000,9999)}@example.com"
    password = "Password123"  # meets 8+ chars, uppercase, lowercase, number
    registro_payload = {
        "nombre": "Test User",
        "email": unique_email,
        "password": password
    }

    user_id = None

    try:
        # 1) Register new user
        headers = {"Content-Type": "application/json"}
        try:
            resp = requests.post(
                f"{BASE_URL}/api/auth/registro",
                json=registro_payload,
                headers=headers,
                timeout=TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            raise AssertionError(f"Request error during registro: {e}")

        assert resp is not None, "No response from registro"
        if resp.status_code != 201:
            # include body for debugging
            raise AssertionError(f"Expected 201 from registro, got {resp.status_code}. Body: {resp.text}")

        try:
            data = resp.json()
        except ValueError:
            raise AssertionError(f"registro response is not valid JSON. Body: {resp.text}")

        assert isinstance(data, dict), "registro response JSON is not an object"
        assert "token" in data and data["token"], "registro response missing token"
        assert "usuario" in data and isinstance(data["usuario"], dict), "registro response missing usuario object"

        usuario = data["usuario"]
        assert usuario.get("email") == unique_email, f"registro usuario email mismatch: expected {unique_email}, got {usuario.get('email')}"

        # Try common id fields
        user_id = usuario.get("_id") or usuario.get("uid") or usuario.get("id")
        assert user_id, f"Could not determine created user id from registro response: {usuario}"

        # 2) Login with the created user
        login_payload = {"email": unique_email, "password": password}
        try:
            login_resp = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=login_payload,
                headers=headers,
                timeout=TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            raise AssertionError(f"Request error during login: {e}")

        assert login_resp is not None, "No response from login"
        if login_resp.status_code != 200:
            raise AssertionError(f"Expected 200 from login, got {login_resp.status_code}. Body: {login_resp.text}")

        try:
            login_data = login_resp.json()
        except ValueError:
            raise AssertionError(f"login response is not valid JSON. Body: {login_resp.text}")

        assert isinstance(login_data, dict), "login response JSON is not an object"
        assert "token" in login_data and isinstance(login_data["token"], str) and login_data["token"].strip(), "login response missing token"
        assert "usuario" in login_data and isinstance(login_data["usuario"], dict), "login response missing usuario object"
        assert login_data["usuario"].get("email") == unique_email, f"login usuario email mismatch: expected {unique_email}, got {login_data['usuario'].get('email')}"

        print("TC002 passed: user successfully logged in and received token and usuario.")

    finally:
        # Cleanup: delete created user using admin token if we have an id
        if user_id:
            try:
                del_headers = {"x-token": ADMIN_TOKEN}
                try:
                    del_resp = requests.delete(
                        f"{BASE_URL}/api/usuarios/{user_id}",
                        headers=del_headers,
                        timeout=TIMEOUT,
                    )
                except requests.exceptions.RequestException as e:
                    print(f"Cleanup: request error during user deletion: {e}", file=sys.stderr)
                    return

                # Expect 200 for successful logical delete
                if del_resp.status_code != 200:
                    print(f"Cleanup: expected 200 deleting user, got {del_resp.status_code}. Body: {del_resp.text}", file=sys.stderr)
                else:
                    try:
                        del_data = del_resp.json()
                        # basic validation of deletion response
                        if isinstance(del_data, dict):
                            if "mensaje" in del_data:
                                # ok
                                pass
                    except ValueError:
                        print("Cleanup: delete response not valid JSON", file=sys.stderr)
            except Exception as e:
                print(f"Unexpected error in cleanup: {e}", file=sys.stderr)


if __name__ == "__main__":
    test_post_api_auth_login_authenticate_user()
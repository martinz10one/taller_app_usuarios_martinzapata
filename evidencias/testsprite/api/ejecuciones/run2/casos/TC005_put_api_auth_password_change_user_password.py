import requests
import uuid
import time
import sys

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
TIMEOUT = 30


def test_put_api_auth_password_change_user_password():
    # Create a new user using admin endpoints so we control the initial password
    unique = str(int(time.time())) + "-" + uuid.uuid4().hex[:8]
    nombre = f"TestUser {unique}"
    email = f"testuser+{unique}@example.com"
    initial_password = "InitPass1A"  # meets 8+ with upper, lower, digit
    new_password = "NewPass2B"       # different valid password

    created_user_id = None

    headers_admin = {
        "x-token": ADMIN_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        # 1) Create user via admin POST /api/usuarios
        payload_create = {
            "nombre": nombre,
            "email": email,
            "password": initial_password,
            "rol": "usuario"
        }
        resp = requests.post(
            f"{BASE_URL}/api/usuarios",
            json=payload_create,
            headers=headers_admin,
            timeout=TIMEOUT
        )
        try:
            data = resp.json()
        except ValueError:
            raise AssertionError(f"Create user: Response is not JSON. Status {resp.status_code}, Body: {resp.text}")

        assert resp.status_code == 201, f"Expected 201 creating user, got {resp.status_code}, body: {data}"

        # Extract user id (handle response being the user object or wrapped)
        if isinstance(data, dict):
            # prefer a wrapped 'usuario' object if present
            user_obj = data.get("usuario") if isinstance(data.get("usuario"), dict) else data
            created_user_id = None
            for key in ("_id", "id", "uid"):
                if key in user_obj:
                    created_user_id = user_obj.get(key)
                    break
        else:
            created_user_id = None

        if not created_user_id:
            raise AssertionError(f"Create user: could not determine created user id from response: {data}")

        assert created_user_id, f"Create user: could not determine created user id from response: {data}"

        # 2) Login as created user to obtain their token
        payload_login = {
            "email": email,
            "password": initial_password
        }
        resp_login = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=payload_login,
            timeout=TIMEOUT
        )
        try:
            login_data = resp_login.json()
        except ValueError:
            raise AssertionError(f"Login: Response is not JSON. Status {resp_login.status_code}, Body: {resp_login.text}")

        assert resp_login.status_code == 200, f"Expected 200 on login, got {resp_login.status_code}, body: {login_data}"
        assert "token" in login_data, f"Login response missing token: {login_data}"
        user_token = login_data["token"]

        # 3) Change password using PUT /api/auth/password with user token
        headers_user = {
            "x-token": user_token,
            "Content-Type": "application/json"
        }
        payload_change = {
            "passwordActual": initial_password,
            "passwordNueva": new_password
        }
        resp_change = requests.put(
            f"{BASE_URL}/api/auth/password",
            json=payload_change,
            headers=headers_user,
            timeout=TIMEOUT
        )
        try:
            change_data = resp_change.json()
        except ValueError:
            raise AssertionError(f"Change password: Response is not JSON. Status {resp_change.status_code}, Body: {resp_change.text}")

        assert resp_change.status_code == 200, f"Expected 200 on password change, got {resp_change.status_code}, body: {change_data}"
        # Expect message 'Contraseña actualizada'
        mensaje = change_data.get("mensaje") if isinstance(change_data, dict) else None
        assert mensaje == "Contraseña actualizada", f"Unexpected mensaje after password change: {change_data}"

        # 4) Verify old password no longer works (login should fail with 401)
        resp_old_login = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": initial_password},
            timeout=TIMEOUT
        )
        # Accept either 401 or 400 depending on API; require non-200
        assert resp_old_login.status_code != 200, f"Old password should not authenticate after change, but got 200. Body: {resp_old_login.text}"

        # 5) Verify new password works
        resp_new_login = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": new_password},
            timeout=TIMEOUT
        )
        try:
            new_login_data = resp_new_login.json()
        except ValueError:
            raise AssertionError(f"New login: Response is not JSON. Status {resp_new_login.status_code}, Body: {resp_new_login.text}")

        assert resp_new_login.status_code == 200, f"Expected 200 logging in with new password, got {resp_new_login.status_code}, body: {new_login_data}"
        assert "token" in new_login_data, f"Login with new password missing token: {new_login_data}"

    except requests.RequestException as e:
        raise AssertionError(f"HTTP request failed: {e}") from e
    finally:
        # Cleanup: delete created user using admin token if created
        if created_user_id:
            try:
                resp_del = requests.delete(
                    f"{BASE_URL}/api/usuarios/{created_user_id}",
                    headers=headers_admin,
                    timeout=TIMEOUT
                )
            except requests.RequestException as e:
                # If deletion fails at network level, raise to indicate cleanup issue
                raise AssertionError(f"Cleanup delete request failed: {e}") from e

            # Attempt to parse JSON for helpful assertion, but don't fail the test solely because delete body shape changed
            try:
                del_data = resp_del.json()
            except ValueError:
                del_data = None

            assert resp_del.status_code == 200, f"Expected 200 deleting created user in cleanup, got {resp_del.status_code}, body: {del_data}"


if __name__ == "__main__":
    try:
        test_put_api_auth_password_change_user_password()
        print("TC005 passed")
    except AssertionError as e:
        print(f"TC005 failed: {e}")
        sys.exit(1)

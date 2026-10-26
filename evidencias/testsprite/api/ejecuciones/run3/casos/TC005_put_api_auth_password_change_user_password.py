import requests
import uuid
import sys

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
TIMEOUT = 30


def _extract_user_id(usuario_obj):
    if not isinstance(usuario_obj, dict):
        raise AssertionError("usuario object is not a dict")
    for key in ("uid", "_id", "id"):
        if key in usuario_obj and usuario_obj[key]:
            return usuario_obj[key]
    # sometimes API returns the id under 'usuario' directly as string
    if isinstance(usuario_obj, str) and usuario_obj:
        return usuario_obj
    raise AssertionError("Could not extract user id from usuario object")


def test_put_api_auth_password_change_user_password():
    # Create unique user data
    unique = uuid.uuid4().hex[:8]
    nombre = f"TestUser_{unique}"
    email = f"testuser_{unique}@example.com"
    initial_password = "Passw0rdA1"  # meets 8-64 with upper, lower, number
    new_password = "NewPassw0rdB2"

    created_user_id = None
    created_user_token = None

    try:
        # 1) Register a new user
        registro_url = f"{BASE_URL}/api/auth/registro"
        registro_payload = {"nombre": nombre, "email": email, "password": initial_password}
        resp = requests.post(registro_url, json=registro_payload, timeout=TIMEOUT)
        try:
            resp_json = resp.json()
        except ValueError:
            raise AssertionError(f"Registro returned non-JSON response: {resp.status_code} {resp.text}")

        assert resp.status_code == 201, f"Expected 201 on registro, got {resp.status_code}: {resp_json}"
        assert "token" in resp_json and resp_json["token"], "Registro response missing token"
        assert "usuario" in resp_json and isinstance(resp_json["usuario"], (dict, str)), "Registro response missing usuario"
        created_user_token = resp_json["token"]
        created_user_id = _extract_user_id(resp_json["usuario"])

        # 2) Change password using PUT /api/auth/password with x-token of the created user
        change_pwd_url = f"{BASE_URL}/api/auth/password"
        headers = {"x-token": created_user_token, "Content-Type": "application/json"}
        change_payload = {"passwordActual": initial_password, "passwordNueva": new_password}
        resp = requests.put(change_pwd_url, json=change_payload, headers=headers, timeout=TIMEOUT)
        try:
            resp_json = resp.json()
        except ValueError:
            raise AssertionError(f"Change password returned non-JSON response: {resp.status_code} {resp.text}")

        assert resp.status_code == 200, f"Expected 200 on password change, got {resp.status_code}: {resp_json}"
        # Expect confirmation message exactly as PRD
        mensaje = resp_json.get("mensaje") or resp_json.get("message")
        assert mensaje == "Contraseña actualizada", f"Unexpected mensaje on password change: {mensaje}"

        # 3) Verify login with new password works
        login_url = f"{BASE_URL}/api/auth/login"
        login_payload = {"email": email, "password": new_password}
        resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        try:
            resp_json = resp.json()
        except ValueError:
            raise AssertionError(f"Login returned non-JSON response: {resp.status_code} {resp.text}")

        assert resp.status_code == 200, f"Expected 200 on login with new password, got {resp.status_code}: {resp_json}"
        assert "token" in resp_json and resp_json["token"], "Login response missing token after password change"

    except requests.RequestException as e:
        raise AssertionError(f"HTTP request failed: {e}") from e

    finally:
        # Cleanup: delete created user using admin token if we have the id
        if created_user_id:
            try:
                delete_url = f"{BASE_URL}/api/usuarios/{created_user_id}"
                headers = {"x-token": ADMIN_TOKEN}
                resp = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
                # Accept 200 as success; if 404 or 400, print for debug but don't fail cleanup
                if resp.status_code not in (200, 404, 400):
                    # raise to surface unexpected deletion responses
                    try:
                        body = resp.json()
                    except ValueError:
                        body = resp.text
                    raise AssertionError(f"Unexpected status code deleting user: {resp.status_code} {body}")
            except requests.RequestException as e:
                # If cleanup fails due to network, raise so test runner sees it
                raise AssertionError(f"Cleanup HTTP request failed: {e}") from e


if __name__ == "__main__":
    try:
        test_put_api_auth_password_change_user_password()
        print("TEST PASSED: TC005 - put api auth password change user password")
    except AssertionError as e:
        print("TEST FAILED: TC005 - put api auth password change user password")
        print(str(e))
        sys.exit(1)
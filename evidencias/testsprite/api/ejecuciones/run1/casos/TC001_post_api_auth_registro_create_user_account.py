import requests
import uuid
import time
import json
import base64
from requests.exceptions import RequestException

BASE_URL = "http://localhost:3000"
TIMEOUT = 30

# Admin token provided in the environment/credentials for cleanup operations
ADMIN_X_TOKEN = "<ADMIN_JWT_REDACTED>"


def _decode_jwt_payload(token):
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload_b64 = parts[1]
        # Pad base64 if necessary
        padding = '=' * (-len(payload_b64) % 4)
        payload_b64 += padding
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return {}


def test_tc001_post_api_auth_registro_create_user_account():
    """
    TC001: Verify that a new user can register with valid nombre, email, and password,
    receiving a 201 status with a token and usuario object without password.
    The created user will be deleted in a finally block using admin credentials.
    """
    register_url = f"{BASE_URL}/api/auth/registro"
    headers = {"Content-Type": "application/json"}
    unique_suffix = uuid.uuid4().hex[:8]
    nombre = f"TestUser {unique_suffix}"
    email = f"testuser_{int(time.time())}_{unique_suffix}@example.com"
    password = "Passw0rd123"  # meets the 8-64, upper, lower, number requirement

    payload = {"nombre": nombre, "email": email, "password": password}

    created_user_id = None
    created_token = None

    try:
        try:
            resp = requests.post(register_url, headers=headers, json=payload, timeout=TIMEOUT)
        except RequestException as e:
            raise AssertionError(f"Request to {register_url} failed: {e}")

        # Expect 201 Created
        assert resp is not None, "No response received from server"
        try:
            resp_json = resp.json()
        except ValueError:
            raise AssertionError(f"Response is not valid JSON. Status code: {resp.status_code}, Body: {resp.text}")

        assert resp.status_code == 201, f"Expected status 201, got {resp.status_code}. Body: {resp_json}"

        # Validate presence of token and usuario
        assert "token" in resp_json and isinstance(resp_json["token"], str) and resp_json["token"].strip() != "", "Response must include a non-empty token"
        assert "usuario" in resp_json and isinstance(resp_json["usuario"], dict), "Response must include a usuario object"

        created_token = resp_json["token"]
        usuario = resp_json["usuario"]

        # The usuario object must not include the password field
        assert "password" not in usuario and usuario.get("password") is None, "Usuario object should not include password"

        # Validate returned nombre and email match what was sent (if provided by API)
        if "nombre" in usuario:
            assert usuario["nombre"] == nombre, f"Returned usuario.nombre mismatch. Expected '{nombre}', got '{usuario['nombre']}'"
        if "email" in usuario:
            assert usuario["email"] == email, f"Returned usuario.email mismatch. Expected '{email}', got '{usuario['email']}'"

        # Extract user id from usuario object or token payload
        created_user_id = usuario.get("uid") or usuario.get("id") or usuario.get("_id")
        if not created_user_id:
            payload_data = _decode_jwt_payload(created_token)
            created_user_id = payload_data.get("uid") or payload_data.get("id")

        assert created_user_id, "Could not determine created user id from response usuario or token payload"

    finally:
        # Cleanup: delete the created user using admin endpoint if we have an id
        if created_user_id:
            delete_url = f"{BASE_URL}/api/usuarios/{created_user_id}"
            delete_headers = {
                "Content-Type": "application/json",
                "x-token": ADMIN_X_TOKEN
            }
            try:
                del_resp = requests.delete(delete_url, headers=delete_headers, timeout=TIMEOUT)
            except RequestException as e:
                raise AssertionError(f"Cleanup DELETE request failed: {e}")

            # Accept 200 as successful logical deletion. If API returns 404 or 400, fail the test to surface issues.
            try:
                del_json = del_resp.json()
            except ValueError:
                del_json = {"text": del_resp.text}

            assert del_resp.status_code == 200, f"Expected 200 on delete cleanup, got {del_resp.status_code}. Body: {del_json}"


if __name__ == "__main__":
    test_tc001_post_api_auth_registro_create_user_account()
    print("TC001 passed.")
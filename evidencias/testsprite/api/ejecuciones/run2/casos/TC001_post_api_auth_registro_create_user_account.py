import requests
import time
import random
import string
import sys
import traceback

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
TIMEOUT = 30


def test_tc001_post_api_auth_registro_create_user_account():
    created_user_id = None
    try:
        # Generate a unique email for the test run
        uniq_suffix = f"{int(time.time())}{random.randint(1000,9999)}"
        email = f"testuser_{uniq_suffix}@example.com"
        nombre = "Test User"
        password = "Aa12345678"  # meets password constraints: uppercase, lowercase, number, length >=8

        registro_url = f"{BASE_URL}/api/auth/registro"
        payload = {
            "nombre": nombre,
            "email": email,
            "password": password
        }

        # First registration attempt: expect success 201 with token and usuario (without password)
        resp = requests.post(registro_url, json=payload, timeout=TIMEOUT)
        try:
            assert resp.status_code == 201, f"Expected 201 on first registration, got {resp.status_code}: {resp.text}"
        except AssertionError:
            # Provide response body for debugging
            raise

        data = resp.json()
        assert isinstance(data, dict), f"Response JSON is not an object: {data}"

        # Validate token presence
        assert "token" in data and isinstance(data["token"], str) and data["token"].strip() != "", "Missing or invalid token in response"

        # Validate usuario object presence
        assert "usuario" in data and isinstance(data["usuario"], dict), f"Missing or invalid 'usuario' in response: {data}"

        usuario = data["usuario"]

        # usuario must not expose password
        assert "password" not in usuario, f"'password' should not be present in usuario, but found: {usuario.get('password')}"

        # Validate returned nombre and email
        assert usuario.get("nombre") == nombre, f"Returned nombre mismatch: expected {nombre}, got {usuario.get('nombre')}"
        assert usuario.get("email") == email, f"Returned email mismatch: expected {email}, got {usuario.get('email')}"

        # Extract user id from common fields
        for key in ("_id", "uid", "id"):
            if key in usuario:
                created_user_id = usuario[key]
                break
        assert created_user_id is not None, f"Could not find user id in usuario object: keys present {list(usuario.keys())}"

        # Second execution to confirm stability: attempt to register the same user again.
        # According to PRD, duplicate email should yield 400.
        resp2 = requests.post(registro_url, json=payload, timeout=TIMEOUT)
        # Accept either 400 or 409 depending on implementation, but prefer 400 per PRD
        assert resp2.status_code in (400, 409), f"Expected 400/409 on duplicate registration, got {resp2.status_code}: {resp2.text}"

        # If server returned JSON, at least ensure it's an error structure
        try:
            data2 = resp2.json()
            assert isinstance(data2, dict), "Duplicate registration response is not JSON object"
        except ValueError:
            # Non-JSON body is acceptable but unexpected
            pass

        print("TC001 passed: registration created user successfully and duplicate registration handled as expected.")

    except Exception:
        print("TC001 failed.")
        traceback.print_exc()
        raise
    finally:
        # Cleanup: delete the created user if we have its id
        if created_user_id:
            delete_url = f"{BASE_URL}/api/usuarios/{created_user_id}"
            headers = {"x-token": ADMIN_TOKEN}
            try:
                resp_del = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
                # Accept 200 (deleted) or 404 (already gone) as acceptable cleanup outcomes
                if resp_del.status_code not in (200, 404):
                    print(f"Warning: unexpected status when deleting test user {created_user_id}: {resp_del.status_code} - {resp_del.text}")
                else:
                    print(f"Cleanup: deleted test user {created_user_id} (status {resp_del.status_code}).")
            except Exception:
                print(f"Cleanup: failed to delete test user {created_user_id}.")
                traceback.print_exc()


if __name__ == "__main__":
    test_tc001_post_api_auth_registro_create_user_account()
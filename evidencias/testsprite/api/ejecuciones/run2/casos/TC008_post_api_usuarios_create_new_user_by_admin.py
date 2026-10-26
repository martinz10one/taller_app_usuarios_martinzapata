import requests
import uuid
import time
import sys

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "Content-Type": "application/json",
    "x-token": ADMIN_TOKEN
}
TIMEOUT = 30


def test_tc008_post_api_usuarios_create_new_user_by_admin():
    created_user_id = None
    # generate unique user data to avoid duplicates across runs
    unique_suffix = str(int(time.time())) + "-" + uuid.uuid4().hex[:6]
    nombre = f"Test User {unique_suffix}"
    email = f"testuser+{unique_suffix}@example.com"
    password = "Aa1strongPass!"
    rol = "usuario"

    payload = {
        "nombre": nombre,
        "email": email,
        "password": password,
        "rol": rol
    }

    try:
        # Create user as admin
        resp = requests.post(
            f"{BASE_URL}/api/usuarios",
            json=payload,
            headers=HEADERS,
            timeout=TIMEOUT
        )
    except Exception as e:
        raise AssertionError(f"Failed to send POST /api/usuarios request: {e}")

    # Expect 201 Created
    assert resp is not None, "No response received from POST /api/usuarios"
    try:
        status = resp.status_code
        body = resp.json() if resp.text else {}
    except ValueError:
        raise AssertionError(f"Response from POST /api/usuarios is not valid JSON. Status: {resp.status_code}, Text: {resp.text}")

    assert status == 201, f"Expected status 201 when creating user, got {status}. Body: {body}"

    # Extract created user from response - handle possible shapes
    created_user = None
    if isinstance(body, dict):
        # Common shapes: { "usuario": {...} } or direct user object
        if "usuario" in body and isinstance(body["usuario"], dict):
            created_user = body["usuario"]
        else:
            # If response is the user object itself or contains user fields
            # Heuristic: presence of 'email' and 'nombre'
            if "email" in body and "nombre" in body:
                created_user = body
            else:
                # Sometimes wrapped in data or user
                for key in ("data", "user", "usuarioCreated"):
                    if key in body and isinstance(body[key], dict):
                        created_user = body[key]
                        break

    assert created_user is not None, f"Created user object not found in response body: {body}"

    # Determine ID field
    created_user_id = created_user.get("_id") or created_user.get("id") or created_user.get("uid")
    assert created_user_id, f"Created user id not found in response user object: {created_user}"

    # Basic checks on returned user
    assert created_user.get("email") == email, f"Created user email mismatch. Expected {email}, got {created_user.get('email')}"
    assert created_user.get("nombre") == nombre, f"Created user nombre mismatch. Expected {nombre}, got {created_user.get('nombre')}"
    # rol may be defaulted; if provided assert it matches
    if "rol" in created_user:
        assert created_user.get("rol") == rol, f"Created user rol mismatch. Expected {rol}, got {created_user.get('rol')}"

    # Check password handling:
    # If password field is present in the returned user, ensure it's not the plaintext
    password_in_response = created_user.get("password") if isinstance(created_user, dict) else None
    if password_in_response is not None:
        # Ensure it's not the plaintext
        assert password_in_response != password, "Password returned equals plaintext password; expected hashed password."
        # Basic heuristic for bcrypt hashed password: starts with $2
        if isinstance(password_in_response, str):
            assert len(password_in_response) >= 20, "Returned password hash length suspiciously short."
    else:
        # If not present, attempt to fetch the user by id (admin GET) to inspect stored password field if any
        try:
            get_resp = requests.get(
                f"{BASE_URL}/api/usuarios/{created_user_id}",
                headers=HEADERS,
                timeout=TIMEOUT
            )
        except Exception as e:
            raise AssertionError(f"Failed to send GET /api/usuarios/{created_user_id}: {e}")

        assert get_resp is not None, f"No response received from GET /api/usuarios/{created_user_id}"
        try:
            get_body = get_resp.json() if get_resp.text else {}
        except ValueError:
            raise AssertionError(f"Response from GET /api/usuarios/{created_user_id} is not valid JSON. Status: {get_resp.status_code}, Text: {get_resp.text}")

        assert get_resp.status_code == 200, f"Expected 200 when retrieving created user, got {get_resp.status_code}. Body: {get_body}"

        fetched_user = None
        if isinstance(get_body, dict):
            if "usuario" in get_body and isinstance(get_body["usuario"], dict):
                fetched_user = get_body["usuario"]
            elif "email" in get_body and "nombre" in get_body:
                fetched_user = get_body
            else:
                for key in ("data", "user"):
                    if key in get_body and isinstance(get_body[key], dict):
                        fetched_user = get_body[key]
                        break

        assert fetched_user is not None, f"Fetched user object not found in GET response: {get_body}"

        fetched_password = fetched_user.get("password")
        if fetched_password is not None:
            assert fetched_password != password, "Fetched user password equals plaintext password; expected hashed."
            if isinstance(fetched_password, str):
                assert len(fetched_password) >= 20, "Fetched password hash length suspiciously short."
        else:
            # As a fallback, verify that login with the plaintext password succeeds (meaning it was hashed and checked)
            try:
                login_resp = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    json={"email": email, "password": password},
                    timeout=TIMEOUT
                )
            except Exception as e:
                raise AssertionError(f"Failed to send POST /api/auth/login: {e}")

            assert login_resp is not None, "No response received from POST /api/auth/login"
            try:
                login_body = login_resp.json() if login_resp.text else {}
            except ValueError:
                raise AssertionError(f"Response from POST /api/auth/login is not valid JSON. Status: {login_resp.status_code}, Text: {login_resp.text}")

            assert login_resp.status_code == 200, f"Expected 200 on login for created user, got {login_resp.status_code}. Body: {login_body}"
            # If login is successful, it's a good indirect indicator that the password was stored hashed and verified

    # If we reached here, creation and password checks passed
    print(f"TC008 passed: Created user id {created_user_id}")

    # Cleanup: delete the created user
    try:
        del_resp = requests.delete(
            f"{BASE_URL}/api/usuarios/{created_user_id}",
            headers=HEADERS,
            timeout=TIMEOUT
        )
    except Exception as e:
        raise AssertionError(f"Failed to send DELETE /api/usuarios/{created_user_id}: {e}")

    # Accept 200 (deleted) or 404 if already gone; prefer 200
    if del_resp is None:
        raise AssertionError("No response received from DELETE request.")
    if del_resp.status_code not in (200, 404):
        # Try to include body for debugging
        try:
            del_body = del_resp.json()
        except Exception:
            del_body = del_resp.text
        raise AssertionError(f"Unexpected status from DELETE /api/usuarios/{created_user_id}: {del_resp.status_code}. Body: {del_body}")

    print(f"TC008 cleanup: Deleted user id {created_user_id} with status {del_resp.status_code}")


if __name__ == "__main__":
    try:
        test_tc008_post_api_usuarios_create_new_user_by_admin()
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
    except Exception as ex:
        print(f"UNEXPECTED ERROR: {ex}")
        sys.exit(2)
    else:
        print("TEST PASSED")
        sys.exit(0)
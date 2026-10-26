import requests
import uuid
import sys
import time

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "x-token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}
TIMEOUT = 30


def test_get_api_usuarios_id_get_user_details_by_id():
    created_user_id = None
    try:
        # Create a new user to retrieve later
        unique_email = f"test.user.{uuid.uuid4().hex[:8]}@example.com"
        create_payload = {
            "nombre": "Test User",
            "email": unique_email,
            "password": "Str0ngPassw0rd",
            "rol": "usuario"
        }

        try:
            resp = requests.post(f"{BASE_URL}/api/usuarios", json=create_payload, headers=HEADERS, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Failed to create user: {e}")

        assert resp is not None, "No response received when creating user"
        if resp.status_code != 201:
            # try to provide response body for debugging
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise AssertionError(f"Expected 201 when creating user, got {resp.status_code}. Response: {body}")

        try:
            body = resp.json()
        except ValueError:
            raise AssertionError("Create user response is not valid JSON")

        # Response might be the user object directly or wrapped. Normalize.
        if isinstance(body, dict) and ("usuario" in body and isinstance(body["usuario"], dict)):
            created = body["usuario"]
        else:
            created = body

        created_user_id = created.get("_id") or created.get("id") or created.get("uid")
        assert created_user_id, f"Created user id not found in response: {created}"

        # Basic checks on created user
        assert created.get("email") == unique_email, f"Created user email mismatch: expected {unique_email}, got {created.get('email')}"
        assert created.get("nombre") == "Test User", f"Created user nombre mismatch: expected 'Test User', got {created.get('nombre')}"
        # rol may be present
        if "rol" in created:
            assert created["rol"] in ("usuario", "admin"), f"Unexpected rol value: {created.get('rol')}"

        # Now retrieve the user by id as admin
        try:
            get_resp = requests.get(f"{BASE_URL}/api/usuarios/{created_user_id}", headers=HEADERS, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Failed to GET user by id: {e}")

        assert get_resp is not None, "No response received when retrieving user by id"
        if get_resp.status_code != 200:
            try:
                get_body = get_resp.json()
            except Exception:
                get_body = get_resp.text
            raise AssertionError(f"Expected 200 when retrieving user by id, got {get_resp.status_code}. Response: {get_body}")

        try:
            get_body = get_resp.json()
        except ValueError:
            raise AssertionError("Get user response is not valid JSON")

        if isinstance(get_body, dict) and ("usuario" in get_body and isinstance(get_body["usuario"], dict)):
            fetched = get_body["usuario"]
        else:
            fetched = get_body

        # Validate fetched fields
        fetched_id = fetched.get("_id") or fetched.get("id") or fetched.get("uid")
        assert fetched_id == created_user_id, f"Fetched user id ({fetched_id}) does not match created id ({created_user_id})"
        assert fetched.get("email") == unique_email, f"Fetched user email ({fetched.get('email')}) does not match expected ({unique_email})"
        assert fetched.get("nombre") == "Test User", f"Fetched user nombre ({fetched.get('nombre')}) does not match expected ('Test User')"
        # Active user expected
        if "estado" in fetched:
            assert fetched["estado"] is True or fetched["estado"] == "true", f"Expected usuario estado to be active, got {fetched.get('estado')}"

        print("TC007 passed: Admin retrieved active user details by id successfully.")

    finally:
        if created_user_id:
            try:
                del_resp = requests.delete(f"{BASE_URL}/api/usuarios/{created_user_id}", headers=HEADERS, timeout=TIMEOUT)
            except requests.RequestException as e:
                raise AssertionError(f"Failed to delete created user in cleanup: {e}")

            # Accept 200 as success; if already deleted or not found, it's an issue but cleanup should attempt to proceed
            if del_resp.status_code != 200:
                try:
                    del_body = del_resp.json()
                except Exception:
                    del_body = del_resp.text
                raise AssertionError(f"Expected 200 when deleting user in cleanup, got {del_resp.status_code}. Response: {del_body}")


if __name__ == "__main__":
    try:
        test_get_api_usuarios_id_get_user_details_by_id()
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(2)
    print("Test completed successfully.")
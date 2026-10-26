import requests
import uuid
import sys

BASE_URL = "http://localhost:3000"
TIMEOUT = 30

# Admin x-token provided by environment/authentication (from instructions)
ADMIN_X_TOKEN = "<ADMIN_JWT_REDACTED>"

def _extract_user(obj):
    if not isinstance(obj, dict):
        return None
    # Common shapes: { "usuario": { ... } } or { "token": "...", "usuario": { ... } } or direct user dict
    if "usuario" in obj and isinstance(obj["usuario"], dict):
        return obj["usuario"]
    # Some endpoints might return the user directly
    # Heuristics: presence of email or nombre fields
    if "email" in obj or "nombre" in obj:
        return obj
    return None

def _extract_user_id(user_obj):
    # Try common id fields
    for key in ("uid", "_id", "id"):
        if isinstance(user_obj, dict) and key in user_obj:
            return user_obj[key]
    return None

def test_put_api_auth_perfil_update_authenticated_user_profile():
    created_user_id = None
    admin_headers = {
        "Content-Type": "application/json",
        "x-token": ADMIN_X_TOKEN
    }

    # Create a new user to act as the authenticated subject
    unique = uuid.uuid4().hex[:8]
    register_payload = {
        "nombre": f"TestUser {unique}",
        "email": f"testuser+{unique}@example.com",
        "password": "Password1A"
    }

    try:
        resp = requests.post(f"{BASE_URL}/api/auth/registro", json=register_payload, headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Registration request failed: {e}")

    try:
        assert resp.status_code == 201, f"Expected 201 from registration, got {resp.status_code}, body: {resp.text}"
        resp_json = resp.json()
    except ValueError:
        raise AssertionError(f"Registration response is not valid JSON. Status: {resp.status_code}, Body: {resp.text}")

    # Extract token and user
    token = resp_json.get("token")
    user_obj = _extract_user(resp_json)
    assert token, f"Registration did not return token. Body: {resp_json}"
    assert user_obj is not None, f"Registration did not return usuario object. Body: {resp_json}"

    created_user_id = _extract_user_id(user_obj)
    # If we couldn't find an id in the returned usuario, try to decode from token? Skip deletion if not found.
    assert created_user_id is not None, f"Could not determine created user id from response usuario: {user_obj}"

    # Prepare update payload: change nombre and email
    new_unique = uuid.uuid4().hex[:6]
    update_payload = {
        "nombre": f"Updated {unique}",
        "email": f"updated+{new_unique}+{unique}@example.com"
    }

    user_headers = {
        "Content-Type": "application/json",
        "x-token": token
    }

    try:
        resp_update = requests.put(f"{BASE_URL}/api/auth/perfil", json=update_payload, headers=user_headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Update request failed: {e}")

    try:
        assert resp_update.status_code == 200, f"Expected 200 from perfil update, got {resp_update.status_code}, body: {resp_update.text}"
        update_json = resp_update.json()
    except ValueError:
        raise AssertionError(f"Update response is not valid JSON. Status: {resp_update.status_code}, Body: {resp_update.text}")

    updated_user = _extract_user(update_json)
    assert updated_user is not None, f"Update response did not contain user object. Body: {update_json}"

    # Validate fields updated
    assert updated_user.get("nombre") == update_payload["nombre"], f"Nombre not updated. Expected {update_payload['nombre']}, got {updated_user.get('nombre')}"
    assert updated_user.get("email") == update_payload["email"], f"Email not updated. Expected {update_payload['email']}, got {updated_user.get('email')}"

    # Optionally verify the id stayed the same
    updated_id = _extract_user_id(updated_user)
    assert updated_id == created_user_id, f"User id changed after update. Before: {created_user_id}, After: {updated_id}"

    print("TC004 passed: authenticated user profile updated successfully.")

    # Cleanup: delete created user using admin token
    try:
        del_resp = requests.delete(f"{BASE_URL}/api/usuarios/{created_user_id}", headers=admin_headers, timeout=TIMEOUT)
        # Expect 200 for successful logical delete
        if del_resp.status_code not in (200,):
            raise AssertionError(f"Cleanup deletion expected status 200, got {del_resp.status_code}, body: {del_resp.text}")
    except requests.RequestException as e:
        raise AssertionError(f"Cleanup deletion request failed: {e}")

if __name__ == "__main__":
    try:
        test_put_api_auth_perfil_update_authenticated_user_profile()
    except AssertionError as e:
        print("Test failed:", e)
        sys.exit(1)
    except Exception as e:
        print("Unexpected error during test:", e)
        sys.exit(2)
    sys.exit(0)
import requests
import uuid
import time
import sys

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "x-token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}
TIMEOUT = 30


def _extract_user_from_response(json_body):
    # Possible shapes: { "usuario": {...} } or {...user fields...}
    if not isinstance(json_body, dict):
        return None
    if "usuario" in json_body and isinstance(json_body["usuario"], dict):
        return json_body["usuario"]
    # sometimes API returns the user directly
    # heuristic: presence of 'email' and 'nombre' or '_id' keys
    if any(k in json_body for k in ("email", "nombre", "_id", "id", "rol")):
        return json_body
    return None


def test_get_api_usuarios_id_get_user_details_by_id_tc007():
    created_user_id = None
    created_user_data = None
    try:
        # 1) Create a new user as admin to ensure we have a valid active user id
        unique_email = f"testuser_{int(time.time())}_{uuid.uuid4().hex[:6]}@example.com"
        create_payload = {
            "nombre": "Test User TC007",
            "email": unique_email,
            # Password meets typical policy: at least 8 chars, upper, lower, number
            "password": "Aa12345678",
            "rol": "usuario"
        }

        resp = requests.post(
            f"{BASE_URL}/api/usuarios",
            headers=HEADERS,
            json=create_payload,
            timeout=TIMEOUT
        )
        try:
            resp_json = resp.json()
        except ValueError:
            resp_json = None

        assert resp.status_code == 201, f"Expected 201 when creating user, got {resp.status_code}, body: {resp_json}"

        user_obj = _extract_user_from_response(resp_json)
        assert user_obj is not None, f"Could not find created user object in response: {resp_json}"

        # Try various id field names
        created_user_id = user_obj.get("_id") or user_obj.get("id") or user_obj.get("uid")
        assert created_user_id, f"Created user id not found in response object: {user_obj}"
        created_user_data = user_obj

        # 2) GET /api/usuarios/:id as admin to retrieve the user details
        get_resp = requests.get(
            f"{BASE_URL}/api/usuarios/{created_user_id}",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        try:
            get_json = get_resp.json()
        except ValueError:
            get_json = None

        assert get_resp.status_code == 200, f"Expected 200 when retrieving user by id, got {get_resp.status_code}, body: {get_json}"

        fetched_user = _extract_user_from_response(get_json)
        assert fetched_user is not None, f"Could not find user object in GET response: {get_json}"

        # Validate key fields match
        # IDs may be in different fields, normalize for comparison
        fetched_id = fetched_user.get("_id") or fetched_user.get("id") or fetched_user.get("uid")
        assert str(fetched_id) == str(created_user_id), f"Fetched user id ({fetched_id}) does not match created id ({created_user_id})"

        # Nombre and email should match what we created
        if "nombre" in fetched_user:
            assert fetched_user["nombre"] == create_payload["nombre"], f"Fetched nombre does not match: expected {create_payload['nombre']}, got {fetched_user.get('nombre')}"
        if "email" in fetched_user:
            assert fetched_user["email"] == create_payload["email"], f"Fetched email does not match: expected {create_payload['email']}, got {fetched_user.get('email')}"
        # Rol should be usuario
        if "rol" in fetched_user:
            assert fetched_user["rol"] == "usuario", f"Fetched rol expected 'usuario', got {fetched_user.get('rol')}"

        print("TC007 passed: Admin can retrieve details of an active user by id and received expected user details.")
    except requests.RequestException as e:
        raise AssertionError(f"HTTP request failed: {e}") from e
    finally:
        # Cleanup: delete the created user if exists
        if created_user_id:
            try:
                del_resp = requests.delete(
                    f"{BASE_URL}/api/usuarios/{created_user_id}",
                    headers=HEADERS,
                    timeout=TIMEOUT
                )
                # Accept either 200 (deleted) or 404 (already not found) as cleanup success
                if del_resp.status_code not in (200, 404):
                    # try to get body for debugging
                    try:
                        body = del_resp.json()
                    except ValueError:
                        body = del_resp.text
                    print(f"Warning: cleanup delete returned unexpected status {del_resp.status_code}, body: {body}", file=sys.stderr)
            except requests.RequestException as e:
                print(f"Warning: cleanup delete request failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    test_get_api_usuarios_id_get_user_details_by_id_tc007()
import requests
import time
import sys

BASE_URL = "http://localhost:3000"
X_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "x-token": X_TOKEN,
    "Content-Type": "application/json"
}
TIMEOUT = 30.0

def _extract_usuario_from_response(json_body):
    if not isinstance(json_body, dict):
        return None
    if "usuario" in json_body and isinstance(json_body["usuario"], dict):
        return json_body["usuario"]
    # sometimes API may return the user object at top-level
    if "nombre" in json_body or "_id" in json_body or "email" in json_body:
        return json_body
    return None

def test_put_api_usuarios_id_update_user_details_by_admin():
    created_user_id = None
    try:
        # 1) Create a new user as admin to be updated later
        timestamp = int(time.time() * 1000)
        new_user = {
            "nombre": f"Test User {timestamp}",
            "email": f"testuser_{timestamp}@example.com",
            "password": "Passw0rd123",
            "rol": "usuario"
        }
        resp = requests.post(
            f"{BASE_URL}/api/usuarios",
            headers=HEADERS,
            json=new_user,
            timeout=TIMEOUT
        )
        try:
            resp_json = resp.json()
        except ValueError:
            assert False, f"Create user: response not JSON, status {resp.status_code}, body: {resp.text}"

        assert resp.status_code == 201, f"Expected 201 when creating user, got {resp.status_code}, body: {resp_json}"

        created_usuario = _extract_usuario_from_response(resp_json)
        assert isinstance(created_usuario, dict), f"Created user object not found in response: {resp_json}"
        # Accept both _id or id as identifier
        created_user_id = created_usuario.get("_id") or created_usuario.get("id") or created_usuario.get("uid")
        assert created_user_id, f"Created user id not found in response: {created_usuario}"
        assert created_usuario.get("email") == new_user["email"]
        assert created_usuario.get("rol") == "usuario"

        # 2) Partially update the created user's nombre and email
        updated_payload = {
            "nombre": f"Updated Name {timestamp}",
            "email": f"updated_{timestamp}@example.com"
            # no password field to ensure password is unchanged
        }
        resp_update = requests.put(
            f"{BASE_URL}/api/usuarios/{created_user_id}",
            headers=HEADERS,
            json=updated_payload,
            timeout=TIMEOUT
        )
        try:
            resp_update_json = resp_update.json()
        except ValueError:
            assert False, f"Update user: response not JSON, status {resp_update.status_code}, body: {resp_update.text}"

        assert resp_update.status_code == 200, f"Expected 200 on update, got {resp_update.status_code}, body: {resp_update_json}"
        updated_usuario = _extract_usuario_from_response(resp_update_json)
        assert isinstance(updated_usuario, dict), f"Updated user object not returned: {resp_update_json}"
        # Check fields updated
        assert updated_usuario.get("nombre") == updated_payload["nombre"], f"Nombre not updated. Expected {updated_payload['nombre']}, got {updated_usuario.get('nombre')}"
        assert updated_usuario.get("email") == updated_payload["email"], f"Email not updated. Expected {updated_payload['email']}, got {updated_usuario.get('email')}"
        # Ensure rol stays the same (usuario)
        assert updated_usuario.get("rol") == "usuario", f"Role unexpectedly changed on partial update: {updated_usuario.get('rol')}"

        # 3) Fetch admin profile to get admin's own id
        resp_admin_profile = requests.get(
            f"{BASE_URL}/api/auth/perfil",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        try:
            resp_admin_profile_json = resp_admin_profile.json()
        except ValueError:
            assert False, f"Admin profile: response not JSON, status {resp_admin_profile.status_code}, body: {resp_admin_profile.text}"

        assert resp_admin_profile.status_code == 200, f"Expected 200 fetching admin profile, got {resp_admin_profile.status_code}, body: {resp_admin_profile_json}"
        admin_usuario = _extract_usuario_from_response(resp_admin_profile_json)
        assert isinstance(admin_usuario, dict), f"Admin user object missing in profile response: {resp_admin_profile_json}"
        admin_id = admin_usuario.get("_id") or admin_usuario.get("id") or admin_usuario.get("uid")
        assert admin_id, f"Admin id not present in profile response: {admin_usuario}"

        # 4) Attempt to change admin's own role - should be forbidden with 400 and specific message
        role_change_payload = {"rol": "usuario"}
        resp_self_role = requests.put(
            f"{BASE_URL}/api/usuarios/{admin_id}",
            headers=HEADERS,
            json=role_change_payload,
            timeout=TIMEOUT
        )
        # It's expected to be a 400 with message "No puedes cambiar tu propio rol"
        try:
            resp_self_role_json = resp_self_role.json()
        except ValueError:
            # If not JSON, still fail
            assert False, f"Self role change: response not JSON, status {resp_self_role.status_code}, body: {resp_self_role.text}"

        assert resp_self_role.status_code == 400, f"Expected 400 when admin attempts to change own role, got {resp_self_role.status_code}, body: {resp_self_role_json}"
        # Check error message presence
        msg = None
        if isinstance(resp_self_role_json, dict):
            # Look for common message fields
            msg = resp_self_role_json.get("msg") or resp_self_role_json.get("mensaje") or resp_self_role_json.get("error") or resp_self_role_json.get("message")
        assert msg is not None, f"Expected an error message in response body when changing own role, got: {resp_self_role_json}"
        assert "No puedes cambiar tu propio rol" in str(msg), f"Unexpected error message when changing own role: {msg}"

    except requests.RequestException as e:
        assert False, f"Request failed with exception: {e}"
    finally:
        # Cleanup: delete the created user if exists
        if created_user_id:
            try:
                resp_del = requests.delete(
                    f"{BASE_URL}/api/usuarios/{created_user_id}",
                    headers=HEADERS,
                    timeout=TIMEOUT
                )
                # if already deleted or not found, it's acceptable for cleanup
                if resp_del.status_code not in (200, 404, 400):
                    # attempt to parse body for debugging
                    try:
                        body = resp_del.json()
                    except ValueError:
                        body = resp_del.text
                    print(f"Warning: unexpected status deleting test user: {resp_del.status_code}, body: {body}", file=sys.stderr)
            except requests.RequestException as e:
                print(f"Warning: failed to delete test user due to exception: {e}", file=sys.stderr)

if __name__ == "__main__":
    test_put_api_usuarios_id_update_user_details_by_admin()
    print("TC009 passed")
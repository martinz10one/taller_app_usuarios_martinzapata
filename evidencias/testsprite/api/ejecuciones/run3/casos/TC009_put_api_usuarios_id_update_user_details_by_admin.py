import requests
import uuid
import json
import sys
from requests.exceptions import RequestException

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
ADMIN_ID = "6adfb2ced9a282feb8c09f27"
TIMEOUT = 30

def _extract_user_id(obj):
    # obj could be a usuario object or wrapped under 'usuario'
    if not isinstance(obj, dict):
        return None
    # If wrapped
    if 'usuario' in obj and isinstance(obj['usuario'], dict):
        obj = obj['usuario']
    for key in ('_id', 'id', 'uid', 'UID', 'Id'):
        if key in obj:
            return obj[key]
    # try typical mongo string id field 'uid' in token style
    if 'uid' in obj:
        return obj['uid']
    return None

def test_TC009_put_api_usuarios_update_by_admin():
    headers = {
        "x-token": ADMIN_TOKEN,
        "Content-Type": "application/json"
    }

    created_user_id = None

    # Create a new user to be updated
    unique = uuid.uuid4().hex[:8]
    new_user_payload = {
        "nombre": f"Test User {unique}",
        "email": f"test+{unique}@example.com",
        "password": "Str0ngPass123",
        "rol": "usuario"
    }

    try:
        try:
            resp = requests.post(
                f"{BASE_URL}/api/usuarios",
                headers=headers,
                json=new_user_payload,
                timeout=TIMEOUT
            )
        except RequestException as e:
            raise AssertionError(f"Failed to create user: {e}")

        assert resp is not None, "No response when creating user"
        assert resp.status_code == 201, f"Expected 201 creating user, got {resp.status_code}, body: {resp.text}"

        try:
            resp_json = resp.json()
        except ValueError:
            raise AssertionError(f"Create user response is not valid JSON: {resp.text}")

        created_user_id = _extract_user_id(resp_json)
        assert created_user_id, f"Could not extract created user id from response: {resp_json}"

        # Partial update of the created user by admin
        update_payload = {
            "nombre": f"Updated Name {unique}",
            "email": f"updated+{unique}@example.com"
            # do not include rol here; only partial fields
        }

        try:
            resp_update = requests.put(
                f"{BASE_URL}/api/usuarios/{created_user_id}",
                headers=headers,
                json=update_payload,
                timeout=TIMEOUT
            )
        except RequestException as e:
            raise AssertionError(f"Failed to update user {created_user_id}: {e}")

        assert resp_update is not None, "No response when updating user"
        assert resp_update.status_code == 200, f"Expected 200 updating user, got {resp_update.status_code}, body: {resp_update.text}"

        try:
            update_json = resp_update.json()
        except ValueError:
            raise AssertionError(f"Update response is not valid JSON: {resp_update.text}")

        # Extract returned user object and verify fields updated
        returned_user = update_json.get("usuario") if isinstance(update_json, dict) and "usuario" in update_json else update_json
        assert isinstance(returned_user, dict), f"Returned user is not an object: {update_json}"

        # Verify updated fields
        assert returned_user.get("nombre") == update_payload["nombre"], f"Nombre not updated. Expected {update_payload['nombre']}, got {returned_user.get('nombre')}"
        assert returned_user.get("email") == update_payload["email"], f"Email not updated. Expected {update_payload['email']}, got {returned_user.get('email')}"

        # Verify rol remains unchanged (should be 'usuario' for created user)
        assert returned_user.get("rol") in ("usuario", "admin"), f"Returned user missing rol: {returned_user}"
        # If rol exists, ensure it's not accidentally elevated to admin
        assert returned_user.get("rol") == "usuario", f"Role unexpectedly changed for created user: {returned_user.get('rol')}"

        # Now attempt to change admin's own role to the opposite role ('usuario') and expect 400
        self_role_change_payload = {"rol": "usuario"}

        try:
            resp_self_change = requests.put(
                f"{BASE_URL}/api/usuarios/{ADMIN_ID}",
                headers=headers,
                json=self_role_change_payload,
                timeout=TIMEOUT
            )
        except RequestException as e:
            raise AssertionError(f"Failed to attempt self role change for admin id {ADMIN_ID}: {e}")

        assert resp_self_change is not None, "No response when admin tried to change own role"
        # According to instructions, trying to change own role to opposite should return 400
        assert resp_self_change.status_code == 400, f"Expected 400 when admin attempts to change own role to 'usuario', got {resp_self_change.status_code}, body: {resp_self_change.text}"

        try:
            self_change_json = resp_self_change.json()
        except ValueError:
            raise AssertionError(f"Self-role-change response is not valid JSON: {resp_self_change.text}")

        # The API should return an error message "No puedes cambiar tu propio rol"
        # It might be under different keys, so search in values
        found_msg = False
        msg_expected = "No puedes cambiar tu propio rol"
        if isinstance(self_change_json, dict):
            # Search for expected message in any string value
            for v in self_change_json.values():
                if isinstance(v, str) and msg_expected in v:
                    found_msg = True
                    break
                if isinstance(v, dict):
                    for vv in v.values():
                        if isinstance(vv, str) and msg_expected in vv:
                            found_msg = True
                            break
                if found_msg:
                    break

        assert found_msg, f"Expected error message '{msg_expected}' in response, got: {self_change_json}"

    finally:
        # Cleanup: delete the created user if exists
        if created_user_id:
            try:
                resp_del = requests.delete(
                    f"{BASE_URL}/api/usuarios/{created_user_id}",
                    headers=headers,
                    timeout=TIMEOUT
                )
                # Accept 200 as successful deletion, 404 if already gone
                if resp_del is not None and resp_del.status_code not in (200, 404):
                    # If deletion failed, raise to surface the issue
                    raise AssertionError(f"Unexpected status deleting user {created_user_id}: {resp_del.status_code}, body: {resp_del.text}")
            except RequestException as e:
                # If delete request failed, raise
                raise AssertionError(f"Failed to delete created user {created_user_id} in cleanup: {e}")

if __name__ == "__main__":
    test_TC009_put_api_usuarios_update_by_admin()
    print("TC009 passed.")
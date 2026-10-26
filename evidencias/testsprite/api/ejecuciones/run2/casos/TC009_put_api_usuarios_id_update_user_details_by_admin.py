import requests
import uuid
import json
import sys

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {"x-token": ADMIN_TOKEN, "Content-Type": "application/json"}
REQUEST_TIMEOUT = 30


def _extract_user(obj):
    # API may return the usuario directly or nested under 'usuario'
    if isinstance(obj, dict):
        if "usuario" in obj and isinstance(obj["usuario"], dict):
            return obj["usuario"]
        return obj
    return None


def _get_id(user_obj):
    for key in ("_id", "uid", "id"):
        if key in user_obj:
            return user_obj[key]
    return None


def test_tc009_put_api_usuarios_id_update_user_details_by_admin():
    # Create a new user to update (resource id not provided)
    unique = uuid.uuid4().hex[:8]
    new_user_payload = {
        "nombre": f"TestUser-{unique}",
        "email": f"testuser.{unique}@example.com",
        "password": "Password123",
        "rol": "usuario"
    }

    created_user = None
    created_user_id = None

    try:
        # Create user (admin)
        resp = requests.post(
            f"{BASE_URL}/api/usuarios",
            headers=HEADERS,
            data=json.dumps(new_user_payload),
            timeout=REQUEST_TIMEOUT,
        )
        assert resp.status_code == 201, f"Expected 201 when creating user, got {resp.status_code}: {resp.text}"
        body = resp.json()
        created_user = _extract_user(body)
        assert isinstance(created_user, dict), f"Created user response malformed: {body}"
        created_user_id = _get_id(created_user)
        assert created_user_id, f"Created user id not found in response: {created_user}"

        # First partial update: change nombre and email, omit password and rol
        update_payload_1 = {
            "nombre": f"UpdatedName-{unique}",
            "email": f"updated.{unique}@example.com"
        }
        resp_update_1 = requests.put(
            f"{BASE_URL}/api/usuarios/{created_user_id}",
            headers=HEADERS,
            data=json.dumps(update_payload_1),
            timeout=REQUEST_TIMEOUT,
        )
        assert resp_update_1.status_code == 200, f"Expected 200 for partial update, got {resp_update_1.status_code}: {resp_update_1.text}"
        body_update_1 = resp_update_1.json()
        updated_user_1 = _extract_user(body_update_1)
        assert isinstance(updated_user_1, dict), f"Updated user response malformed: {body_update_1}"
        updated_id_1 = _get_id(updated_user_1)
        assert updated_id_1 == created_user_id, "User ID changed after update"
        assert updated_user_1.get("nombre") == update_payload_1["nombre"], "Nombre was not updated"
        assert updated_user_1.get("email") == update_payload_1["email"], "Email was not updated"

        # Second execution (repeat the update with a new name/email) to confirm stability
        update_payload_2 = {
            "nombre": f"UpdatedName2-{unique}",
            "email": f"updated2.{unique}@example.com"
        }
        resp_update_2 = requests.put(
            f"{BASE_URL}/api/usuarios/{created_user_id}",
            headers=HEADERS,
            data=json.dumps(update_payload_2),
            timeout=REQUEST_TIMEOUT,
        )
        assert resp_update_2.status_code == 200, f"Expected 200 for second partial update, got {resp_update_2.status_code}: {resp_update_2.text}"
        body_update_2 = resp_update_2.json()
        updated_user_2 = _extract_user(body_update_2)
        assert isinstance(updated_user_2, dict), f"Second updated user response malformed: {body_update_2}"
        updated_id_2 = _get_id(updated_user_2)
        assert updated_id_2 == created_user_id, "User ID changed after second update"
        assert updated_user_2.get("nombre") == update_payload_2["nombre"], "Nombre was not updated on second update"
        assert updated_user_2.get("email") == update_payload_2["email"], "Email was not updated on second update"

        # Verify admin cannot change their own role
        # Extract admin id from token payload as given in PRD token (uid present), fallback attempt to query profile
        admin_id = None
        # token payload shows uid; we'll try to obtain admin id by calling profile endpoint
        resp_profile = requests.get(f"{BASE_URL}/api/auth/perfil", headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp_profile.status_code == 200:
            admin_profile = resp_profile.json()
            admin_obj = _extract_user(admin_profile)
            admin_id = _get_id(admin_obj)
        else:
            # If profile fails, try to parse from token (best-effort)
            # As a fallback, attempt to decode token segments to extract uid (not verifying), but keep simple:
            # Use the uid embedded in the token per instruction if available
            # Hardcode from known token payload per test environment
            admin_id = "6adfb2ced9a282feb8c09f27"

        assert admin_id, "Unable to determine admin id for self-role-change test"

        change_role_payload = {"rol": "usuario" if created_user.get("rol") == "admin" else "admin"}
        resp_self_role = requests.put(
            f"{BASE_URL}/api/usuarios/{admin_id}",
            headers=HEADERS,
            data=json.dumps(change_role_payload),
            timeout=REQUEST_TIMEOUT,
        )
        # Expecting 400 with message 'No puedes cambiar tu propio rol'
        assert resp_self_role.status_code == 400, f"Expected 400 when admin attempts to change own role, got {resp_self_role.status_code}: {resp_self_role.text}"
        body_self_role = resp_self_role.json()
        # Accept either direct message or nested error format
        msg_found = False
        if isinstance(body_self_role, dict):
            # check common fields
            for v in body_self_role.values():
                if isinstance(v, str) and "No puedes cambiar tu propio rol" in v:
                    msg_found = True
                    break
            # sometimes message under 'msg' or 'mensaje'
            if not msg_found:
                for key in ("msg", "mensaje", "message", "error"):
                    if key in body_self_role and isinstance(body_self_role[key], str):
                        if "No puedes cambiar tu propio rol" in body_self_role[key]:
                            msg_found = True
                            break
        assert msg_found, f"Expected error message 'No puedes cambiar tu propio rol' in response: {body_self_role}"

        print("TC009 passed")
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        raise
    finally:
        # Cleanup: delete created user if exists
        if created_user_id:
            try:
                resp_del = requests.delete(
                    f"{BASE_URL}/api/usuarios/{created_user_id}",
                    headers=HEADERS,
                    timeout=REQUEST_TIMEOUT,
                )
                # Accept 200 for successful logical delete or 404 if already deleted/nonexistent
                if resp_del.status_code not in (200, 404):
                    # If deletion failed, raise to surface the issue
                    raise AssertionError(f"Unexpected status when deleting user {created_user_id}: {resp_del.status_code}: {resp_del.text}")
            except requests.RequestException as e:
                print(f"Cleanup delete request failed: {e}", file=sys.stderr)
                raise


if __name__ == "__main__":
    test_tc009_put_api_usuarios_id_update_user_details_by_admin()
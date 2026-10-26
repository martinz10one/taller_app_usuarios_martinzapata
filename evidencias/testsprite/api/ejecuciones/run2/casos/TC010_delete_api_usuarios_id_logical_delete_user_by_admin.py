import requests
import json
import time
import uuid
import sys

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "x-token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}
TIMEOUT = 30


def test_TC010_delete_api_usuarios_id_logical_delete_user_by_admin():
    created_user_id = None
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        # 1) Get admin profile to obtain admin id
        resp = session.get(f"{BASE_URL}/api/auth/perfil", timeout=TIMEOUT)
        try:
            resp_json = resp.json()
        except ValueError:
            raise AssertionError(f"Expected JSON response for admin profile, got status {resp.status_code}")

        assert resp.status_code == 200, f"Expected 200 for admin profile, got {resp.status_code}, body: {resp_json}"

        # Perfil may return the user object directly or wrapped under 'usuario'
        if isinstance(resp_json, dict) and "usuario" in resp_json:
            admin_obj = resp_json["usuario"]
        else:
            admin_obj = resp_json

        # admin id could be in _id or id or uid
        admin_id = admin_obj.get("_id") or admin_obj.get("id") or admin_obj.get("uid")
        assert admin_id, f"Could not determine admin id from profile response: {admin_obj}"

        # 2) Create a new user to be deleted (admin creates)
        unique_suffix = str(int(time.time())) + "-" + uuid.uuid4().hex[:6]
        new_user_payload = {
            "nombre": f"TC010 User {unique_suffix}",
            "email": f"tc010-{unique_suffix}@example.com",
            "password": "Aa12345678",
            "rol": "usuario"
        }

        resp = session.post(f"{BASE_URL}/api/usuarios", data=json.dumps(new_user_payload), timeout=TIMEOUT)
        try:
            resp_json = resp.json()
        except ValueError:
            raise AssertionError(f"Expected JSON response when creating user, got status {resp.status_code}")

        assert resp.status_code == 201, f"Expected 201 when creating user, got {resp.status_code}, body: {resp_json}"

        # created user may be returned directly or under 'usuario'
        if isinstance(resp_json, dict) and "usuario" in resp_json:
            created_user = resp_json["usuario"]
        else:
            created_user = resp_json

        created_user_id = created_user.get("_id") or created_user.get("id") or created_user.get("uid")
        assert created_user_id, f"Created user response missing id: {created_user}"

        # 3) Admin deletes the created user (logical delete)
        resp = session.delete(f"{BASE_URL}/api/usuarios/{created_user_id}", timeout=TIMEOUT)
        try:
            delete_json = resp.json()
        except ValueError:
            raise AssertionError(f"Expected JSON response when deleting user, got status {resp.status_code}")

        assert resp.status_code == 200, f"Expected 200 when deleting user, got {resp.status_code}, body: {delete_json}"

        # Expect message and usuario with estado false
        mensaje = delete_json.get("mensaje") if isinstance(delete_json, dict) else None
        usuario_obj = delete_json.get("usuario") if isinstance(delete_json, dict) else None

        assert mensaje is not None, f"Delete response missing 'mensaje': {delete_json}"
        # Accept either exact message or substring
        assert "Usuario" in mensaje or "elimin" in mensaje or "eliminado" in mensaje.lower(), f"Unexpected delete mensaje: {mensaje}"

        assert usuario_obj and isinstance(usuario_obj, dict), f"Delete response missing 'usuario' object: {delete_json}"
        usuario_id_after = usuario_obj.get("_id") or usuario_obj.get("id") or usuario_obj.get("uid")
        assert usuario_id_after == created_user_id, f"Deleted usuario id mismatch: expected {created_user_id}, got {usuario_id_after}"

        # estado field check - could be 'estado' boolean or 'active'/'activo'
        if "estado" in usuario_obj:
            assert usuario_obj["estado"] is False, f"Expected usuario.estado False after deletion, got {usuario_obj['estado']}"
        elif "activo" in usuario_obj:
            assert usuario_obj["activo"] is False, f"Expected usuario.activo False after deletion, got {usuario_obj['activo']}"
        elif "active" in usuario_obj:
            assert usuario_obj["active"] is False, f"Expected usuario.active False after deletion, got {usuario_obj['active']}"
        else:
            # If no explicit flag present, at least the usuario object should contain something indicating deletion.
            pass

        # Since the user is deleted now, mark created_user_id as None to avoid cleanup attempt
        created_user_id = None

        # 4) Attempt to delete admin's own account - should fail with 400 and specific message
        resp = session.delete(f"{BASE_URL}/api/usuarios/{admin_id}", timeout=TIMEOUT)
        # Try parse response
        try:
            self_delete_json = resp.json()
        except ValueError:
            self_delete_json = None

        assert resp.status_code == 400, f"Expected 400 when admin attempts to delete own account, got {resp.status_code}, body: {self_delete_json}"

        # Check message contains expected phrase
        if isinstance(self_delete_json, dict):
            msg = self_delete_json.get("mensaje") or self_delete_json.get("msg") or self_delete_json.get("error") or ""
            assert "No puedes eliminar" in msg or "propia" in msg or "propia cuenta" in msg or "No puedes eliminar tu propia cuenta" in msg, \
                f"Unexpected message when deleting own account: {msg}"
        else:
            # If no JSON body, still fail the test
            raise AssertionError(f"Expected JSON error body when admin deletes own account, got raw response with status {resp.status_code}")

        print("TC010 passed: admin can logically delete another user and cannot delete their own account.")

    except requests.RequestException as e:
        raise AssertionError(f"HTTP request failed: {e}") from e

    finally:
        # Cleanup: if created_user_id still exists (deletion in test failed), attempt to delete it
        if created_user_id:
            try:
                cleanup_resp = session.delete(f"{BASE_URL}/api/usuarios/{created_user_id}", timeout=TIMEOUT)
                # ignore outcome; just attempt cleanup
            except requests.RequestException:
                pass


if __name__ == "__main__":
    try:
        test_TC010_delete_api_usuarios_id_logical_delete_user_by_admin()
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        sys.exit(2)
    else:
        print("TEST SUCCESS")
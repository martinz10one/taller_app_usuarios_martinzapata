import requests
import uuid
import time
import sys

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
TIMEOUT = 30

def _get_json(resp):
    try:
        return resp.json()
    except ValueError:
        return None

def _extract_message(j):
    if not isinstance(j, dict):
        return None
    for key in ("mensaje", "msg", "error", "message"):
        if key in j:
            return j[key]
    return None

def test_tc010_delete_user_by_admin():
    headers = {
        "x-token": ADMIN_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    created_user_id = None
    try:
        # 1) Create a new user as admin to delete later
        unique_email = f"test.user.{uuid.uuid4().hex}@example.com"
        create_payload = {
            "nombre": "Test User",
            "email": unique_email,
            "password": "Password1",
            "rol": "usuario"
        }
        resp = requests.post(f"{BASE_URL}/api/usuarios", json=create_payload, headers=headers, timeout=TIMEOUT)
        assert resp.status_code == 201, f"Expected 201 when creating user, got {resp.status_code}, body: {resp.text}"
        create_json = _get_json(resp)
        assert create_json is not None, "Create user response is not valid JSON"

        # The API might return the usuario directly or nested under 'usuario'
        if isinstance(create_json, dict) and "usuario" in create_json:
            usuario_obj = create_json["usuario"]
        else:
            usuario_obj = create_json

        assert isinstance(usuario_obj, dict), f"Unexpected created usuario format: {usuario_obj}"
        # Try common id fields
        created_user_id = usuario_obj.get("uid") or usuario_obj.get("id") or usuario_obj.get("_id")
        assert created_user_id, f"Created user id not found in response: {usuario_obj}"

        # 2) Delete the created user (logical delete) as admin
        del_resp = requests.delete(f"{BASE_URL}/api/usuarios/{created_user_id}", headers=headers, timeout=TIMEOUT)
        assert del_resp.status_code == 200, f"Expected 200 when deleting user, got {del_resp.status_code}, body: {del_resp.text}"
        del_json = _get_json(del_resp)
        assert isinstance(del_json, dict), f"Delete response is not JSON: {del_resp.text}"

        mensaje = _extract_message(del_json)
        assert mensaje is not None, f"'mensaje' not found in delete response: {del_json}"
        assert "Usuario eliminado" in str(mensaje), f"Unexpected delete message: {mensaje}"

        # Verify returned usuario is deactivated (logical delete -> estado false)
        returned_usuario = del_json.get("usuario")
        assert isinstance(returned_usuario, dict), f"'usuario' field missing or not an object: {del_json}"
        # Possible field names for state
        estado = returned_usuario.get("estado")
        assert estado is False, f"Expected usuario.estado to be False after deletion, got {estado} in {returned_usuario}"

        # 3) Verify admin cannot delete their own account
        # First get admin profile to obtain admin id
        perfil_resp = requests.get(f"{BASE_URL}/api/auth/perfil", headers=headers, timeout=TIMEOUT)
        assert perfil_resp.status_code == 200, f"Expected 200 when fetching admin profile, got {perfil_resp.status_code}, body: {perfil_resp.text}"
        perfil_json = _get_json(perfil_resp)
        assert isinstance(perfil_json, dict), f"Admin profile response not JSON: {perfil_resp.text}"
        # perfil endpoint likely returns the user object directly
        admin_obj = perfil_json
        admin_id = admin_obj.get("uid") or admin_obj.get("id") or admin_obj.get("_id")
        assert admin_id, f"Admin id not found in profile response: {admin_obj}"

        # Attempt to delete own admin account
        del_self_resp = requests.delete(f"{BASE_URL}/api/usuarios/{admin_id}", headers=headers, timeout=TIMEOUT)
        # According to PRD, should return 400 with message 'No puedes eliminar tu propia cuenta'
        assert del_self_resp.status_code == 400, f"Expected 400 when admin attempts to delete own account, got {del_self_resp.status_code}, body: {del_self_resp.text}"
        del_self_json = _get_json(del_self_resp)
        assert isinstance(del_self_json, dict), f"Self-delete response not JSON: {del_self_resp.text}"
        self_msg = _extract_message(del_self_json)
        assert self_msg is not None, f"No message in self-delete response: {del_self_json}"
        assert "propia" in str(self_msg) or "propio" in str(self_msg) or "No puedes eliminar" in str(self_msg), f"Unexpected self-delete message: {self_msg}"

    except AssertionError:
        raise
    except Exception as e:
        # Re-raise exceptions so test frameworks catch failures
        raise
    finally:
        # Cleanup: ensure created user is deleted (ignore errors)
        if created_user_id:
            try:
                requests.delete(f"{BASE_URL}/api/usuarios/{created_user_id}", headers=headers, timeout=TIMEOUT)
            except Exception:
                pass

if __name__ == "__main__":
    try:
        test_tc010_delete_user_by_admin()
        print("TC010 passed")
    except AssertionError as e:
        print("TC010 failed:", e)
        sys.exit(1)
    except Exception as e:
        print("TC010 error:", e)
        sys.exit(2)
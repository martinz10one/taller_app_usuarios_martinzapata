import requests
import time
import json

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
ADMIN_ID = "6adfb2ced9a282feb8c09f27"  # extracted from provided JWT in test metadata
HEADERS = {
    "x-token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}
TIMEOUT = 30


def test_delete_api_usuarios_id_logical_delete_user_by_admin_tc010():
    created_user_id = None
    # 1) Create a new user to be deleted by admin
    unique_suffix = str(int(time.time() * 1000))
    new_user_payload = {
        "nombre": f"TC010 User {unique_suffix}",
        "email": f"tc010_{unique_suffix}@example.com",
        "password": "Aa12345678",
        "rol": "usuario"
    }
    try:
        resp_create = requests.post(
            f"{BASE_URL}/api/usuarios",
            headers=HEADERS,
            data=json.dumps(new_user_payload),
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        raise AssertionError(f"Request to create user failed: {e}")

    # Expect 201 Created
    assert resp_create.status_code == 201, f"Expected 201 on user creation, got {resp_create.status_code}, body: {resp_create.text}"
    try:
        create_data = resp_create.json()
    except ValueError:
        raise AssertionError(f"Create response is not valid JSON: {resp_create.text}")

    # Extract created user object robustly
    if isinstance(create_data, dict) and "usuario" in create_data:
        created_user = create_data["usuario"]
    else:
        created_user = create_data

    # possible id fields
    created_user_id = (
        created_user.get("uid")
        or created_user.get("_id")
        or created_user.get("id")
        or None
    )
    assert created_user_id, f"Could not determine created user id from response: {create_data}"

    # 2) Admin deletes the created user (logical delete) -> expect 200 and confirmation + deactivated user
    try:
        resp_delete = requests.delete(
            f"{BASE_URL}/api/usuarios/{created_user_id}",
            headers=HEADERS,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        raise AssertionError(f"Request to delete created user failed: {e}")

    assert resp_delete.status_code == 200, f"Expected 200 when admin deletes another user, got {resp_delete.status_code}, body: {resp_delete.text}"
    try:
        delete_data = resp_delete.json()
    except ValueError:
        raise AssertionError(f"Delete response is not valid JSON: {resp_delete.text}")

    # Validate confirmation message exists and usuario is deactivated
    mensaje = None
    if isinstance(delete_data, dict):
        mensaje = delete_data.get("mensaje") or delete_data.get("msg") or delete_data.get("message")
    assert mensaje is not None, f"No confirmation message found in delete response: {delete_data}"
    assert "Usuario eliminado" in str(mensaje) or "eliminado" in str(mensaje), f"Unexpected delete mensaje: {mensaje}"

    # Extract returned usuario
    returned_usuario = None
    if isinstance(delete_data, dict) and "usuario" in delete_data:
        returned_usuario = delete_data["usuario"]
    elif isinstance(delete_data, dict):
        # maybe the API returned the usuario directly
        # if delete_data has id-like fields, treat it as usuario
        if any(k in delete_data for k in ("_id", "uid", "id", "email")):
            returned_usuario = delete_data

    assert returned_usuario is not None, f"Delete response did not include usuario: {delete_data}"

    # Check that the usuario is deactivated (estado/estado flag false)
    usuario_estado = returned_usuario.get("estado") if isinstance(returned_usuario, dict) else None
    # Some APIs may use 'estado' boolean, others 'active' or 'activo'
    if usuario_estado is None:
        usuario_estado = returned_usuario.get("activo") if isinstance(returned_usuario, dict) else None
    if usuario_estado is None:
        usuario_estado = returned_usuario.get("active") if isinstance(returned_usuario, dict) else None

    assert usuario_estado is False, f"Expected usuario to be deactivated (false), got {usuario_estado}, usuario: {returned_usuario}"

    # 3) Admin attempts to delete their own account -> expect 400 with specific error
    try:
        resp_self_delete = requests.delete(
            f"{BASE_URL}/api/usuarios/{ADMIN_ID}",
            headers=HEADERS,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        raise AssertionError(f"Request for admin self-delete failed: {e}")

    # Expect 400 Bad Request
    assert resp_self_delete.status_code == 400, f"Expected 400 when admin attempts to delete own account, got {resp_self_delete.status_code}, body: {resp_self_delete.text}"
    try:
        self_delete_data = resp_self_delete.json()
    except ValueError:
        raise AssertionError(f"Self-delete response is not valid JSON: {resp_self_delete.text}")

    # Determine message field
    self_delete_msg = None
    if isinstance(self_delete_data, dict):
        self_delete_msg = self_delete_data.get("msg") or self_delete_data.get("mensaje") or self_delete_data.get("error") or self_delete_data.get("message")

    assert self_delete_msg is not None, f"No error message found in self-delete response: {self_delete_data}"
    assert "No puedes eliminar tu propia cuenta" in str(self_delete_msg), f"Unexpected self-delete error message: {self_delete_msg}"

    # If we reached here, the test passed for creation deletion and self-delete protection.


if __name__ == "__main__":
    test_delete_api_usuarios_id_logical_delete_user_by_admin_tc010()
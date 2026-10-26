import requests
import time
import random
import string
import sys
import traceback

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "x-token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}
TIMEOUT = 30


def _extract_usuario_from_response(json_body):
    # Response may be { usuario: { ... } } or directly the user object
    if not isinstance(json_body, dict):
        return None
    if "usuario" in json_body and isinstance(json_body["usuario"], dict):
        return json_body["usuario"]
    # Some endpoints may return the user object at top level
    # Try common keys
    for key in ("user", "data",):
        if key in json_body and isinstance(json_body[key], dict):
            return json_body[key]
    # If the json contains user-like keys, assume it's the user
    if any(k in json_body for k in ("nombre", "email", "rol")):
        return json_body
    return None


def _get_id_from_usuario(usuario):
    if not usuario:
        return None
    for k in ("uid", "id", "_id"):
        if k in usuario:
            return usuario[k]
    return None


def test_tc006_list_users_admin():
    created_user_id = None
    created_user_email = None
    created_user_nombre = None

    # Create a new user so we can test search/role/pagination deterministically
    unique_suffix = str(int(time.time())) + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    created_user_nombre = f"TestUser {unique_suffix}"
    created_user_email = f"testuser_{unique_suffix}@example.com"
    create_payload = {
        "nombre": created_user_nombre,
        "email": created_user_email,
        "password": "Aa12345678",
        "rol": "usuario"
    }

    try:
        # Create user
        resp = requests.post(
            f"{BASE_URL}/api/usuarios",
            headers=HEADERS,
            json=create_payload,
            timeout=TIMEOUT
        )
        assert resp.status_code == 201, f"Expected 201 when creating user, got {resp.status_code}, body: {resp.text}"
        resp_json = resp.json()
        usuario = _extract_usuario_from_response(resp_json)
        assert usuario is not None, f"Could not find created usuario in response: {resp_json}"
        created_user_id = _get_id_from_usuario(usuario)
        assert created_user_id, f"Created user id not found in usuario: {usuario}"
        # Basic sanity checks on created user
        assert usuario.get("email") == created_user_email
        assert usuario.get("nombre") == created_user_nombre
        # Ensure password is not returned
        assert "password" not in usuario and "passwd" not in usuario, "Password should not be returned in usuario object"

        # 1) Basic listing without query params
        resp = requests.get(
            f"{BASE_URL}/api/usuarios",
            headers={"x-token": ADMIN_TOKEN},
            timeout=TIMEOUT
        )
        assert resp.status_code == 200, f"Expected 200 for GET /api/usuarios, got {resp.status_code}, body: {resp.text}"
        list_json = resp.json()
        # Validate required pagination keys
        for key in ("total", "pagina", "limite", "totalPaginas", "usuarios"):
            assert key in list_json, f"Key '{key}' missing in list response: {list_json.keys()}"
        assert isinstance(list_json["total"], int)
        assert isinstance(list_json["pagina"], int)
        assert isinstance(list_json["limite"], int)
        assert isinstance(list_json["totalPaginas"], int)
        assert isinstance(list_json["usuarios"], list)
        usuarios_list = list_json["usuarios"]
        # Validate ordering by nombre (non-decreasing, case-insensitive)
        nombres = [u.get("nombre", "").lower() for u in usuarios_list]
        assert nombres == sorted(nombres), "Usuarios are not ordered by nombre ascending"

        # 2) Search by part of the created user's nombre
        buscar_term = created_user_nombre.split()[0]  # use "TestUser"
        resp = requests.get(
            f"{BASE_URL}/api/usuarios",
            headers={"x-token": ADMIN_TOKEN},
            params={"buscar": buscar_term},
            timeout=TIMEOUT
        )
        assert resp.status_code == 200, f"Expected 200 for GET /api/usuarios with buscar, got {resp.status_code}, body: {resp.text}"
        search_json = resp.json()
        assert "usuarios" in search_json and isinstance(search_json["usuarios"], list)
        found = False
        for u in search_json["usuarios"]:
            # match by email or nombre containing the buscar term (case-insensitive)
            if buscar_term.lower() in (u.get("nombre") or "").lower() or buscar_term.lower() in (u.get("email") or "").lower():
                # We expect at least our created user to appear
                if (u.get("email") or "").lower() == created_user_email.lower():
                    found = True
        assert found, f"Created user not found in search results for buscar='{buscar_term}': {search_json['usuarios']}"

        # 3) Filter by role 'usuario' - all returned users should have rol == 'usuario'
        resp = requests.get(
            f"{BASE_URL}/api/usuarios",
            headers={"x-token": ADMIN_TOKEN},
            params={"rol": "usuario", "limite": 50},
            timeout=TIMEOUT
        )
        assert resp.status_code == 200, f"Expected 200 for GET /api/usuarios with rol filter, got {resp.status_code}, body: {resp.text}"
        rol_json = resp.json()
        assert "usuarios" in rol_json and isinstance(rol_json["usuarios"], list)
        usuarios_rol = rol_json["usuarios"]
        assert any((u.get("email") or "").lower() == created_user_email.lower() for u in usuarios_rol), "Created usuario not present in rol=usuario filtered results"
        for u in usuarios_rol:
            rol_val = u.get("rol")
            assert rol_val in ("usuario", "admin"), f"Unexpected rol value in result: {rol_val}"
            assert rol_val == "usuario", f"User with rol != 'usuario' returned when filtering rol=usuario: {u}"

        # 4) Pagination: request pagina=1, limite=1 and validate response pagination metadata and usuarios length
        resp = requests.get(
            f"{BASE_URL}/api/usuarios",
            headers={"x-token": ADMIN_TOKEN},
            params={"pagina": 1, "limite": 1},
            timeout=TIMEOUT
        )
        assert resp.status_code == 200, f"Expected 200 for GET /api/usuarios with pagination, got {resp.status_code}, body: {resp.text}"
        page_json = resp.json()
        assert page_json.get("pagina") == 1, f"Expected pagina == 1, got {page_json.get('pagina')}"
        assert page_json.get("limite") == 1, f"Expected limite == 1, got {page_json.get('limite')}"
        assert isinstance(page_json.get("usuarios"), list)
        assert len(page_json.get("usuarios")) <= 1, "Expected at most 1 user in usuarios for limite=1"

    except AssertionError:
        traceback.print_exc()
        raise
    except Exception:
        traceback.print_exc()
        raise
    finally:
        # Cleanup: delete created user if exists
        if created_user_id:
            # Construct delete endpoint using id; assume API accepts /api/usuarios/:id
            try:
                del_resp = requests.delete(
                    f"{BASE_URL}/api/usuarios/{created_user_id}",
                    headers={"x-token": ADMIN_TOKEN},
                    timeout=TIMEOUT
                )
                # If delete returned 200 or 404 in case it's already gone, accept both but assert no server error
                if del_resp.status_code not in (200, 404, 400):
                    # Print info and raise to surface unexpected delete failure
                    raise AssertionError(f"Unexpected status deleting created user: {del_resp.status_code}, body: {del_resp.text}")
            except Exception:
                # Print but do not mask original exceptions
                print("Error during cleanup deletion of created user:", file=sys.stderr)
                traceback.print_exc()


if __name__ == "__main__":
    test_tc006_list_users_admin()
    print("TC006 passed")
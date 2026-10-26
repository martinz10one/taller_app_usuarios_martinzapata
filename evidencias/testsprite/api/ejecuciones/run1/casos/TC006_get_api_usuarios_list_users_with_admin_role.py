import requests
import time
import uuid
import sys

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "x-token": ADMIN_TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json"
}
TIMEOUT = 30

def _extract_user_id(obj):
    if not isinstance(obj, dict):
        return None
    for key in ("_id", "id", "uid"):
        if key in obj:
            return obj[key]
    return None

def test_tc006_list_users_admin():
    created_user_ids = []
    created_users = []
    try:
        # Create multiple users to ensure listing, ordering, search and role filter can be tested
        timestamp = int(time.time())
        users_to_create = [
            {"nombre": "Alice Test", "email": f"alice.{timestamp}.{uuid.uuid4().hex[:6]}@example.test", "password": "Aa12345678", "rol": "usuario"},
            {"nombre": "Bob Test",   "email": f"bob.{timestamp}.{uuid.uuid4().hex[:6]}@example.test",   "password": "Bb12345678", "rol": "usuario"},
            {"nombre": "Charlie Test", "email": f"charlie.{timestamp}.{uuid.uuid4().hex[:6]}@example.test", "password": "Cc12345678", "rol": "admin"}
        ]

        for u in users_to_create:
            resp = None
            try:
                resp = requests.post(f"{BASE_URL}/api/usuarios", json=u, headers=HEADERS, timeout=TIMEOUT)
            except requests.RequestException as e:
                assert False, f"Request to create user failed: {e}"
            assert resp is not None, "No response when creating user"
            assert resp.status_code in (200,201), f"Expected 200 or 201 creating user, got {resp.status_code}, body: {resp.text}"
            body = resp.json() if resp.content else {}
            # API may return the user directly or wrapped. Try to find the user object.
            user_obj = body.get("usuario") if isinstance(body, dict) and "usuario" in body else body
            user_id = _extract_user_id(user_obj)
            assert user_id, f"Created user id not found in response: {body}"
            created_user_ids.append(user_id)
            created_users.append({"id": user_id, "nombre": user_obj.get("nombre"), "email": user_obj.get("email"), "rol": user_obj.get("rol")})

        # 1) Basic listing without filters
        try:
            resp = requests.get(f"{BASE_URL}/api/usuarios", headers=HEADERS, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Request to list users failed: {e}"
        assert resp.status_code == 200, f"Expected 200 from GET /api/usuarios, got {resp.status_code}, body: {resp.text}"
        list_body = resp.json()
        assert isinstance(list_body, dict), "List response is not a JSON object"
        for key in ("total", "pagina", "limite", "totalPaginas", "usuarios"):
            assert key in list_body, f"Key '{key}' missing in list response"
        usuarios = list_body["usuarios"]
        assert isinstance(usuarios, list), "'usuarios' should be a list"
        # Ensure at least the created users are counted in total
        assert list_body["total"] >= len(created_user_ids), f"Total {list_body['total']} is less than created users {len(created_user_ids)}"
        # Validate ordering by nombre (ascending)
        nombres = [u.get("nombre") for u in usuarios if u.get("nombre") is not None]
        sorted_nombres = sorted(nombres, key=lambda s: s.lower())
        assert nombres == sorted_nombres, "Usuarios list is not ordered by 'nombre' ascending"

        # 2) Search by name (buscar) - should find "Bob Test"
        params = {"buscar": "Bob"}
        try:
            resp = requests.get(f"{BASE_URL}/api/usuarios", headers=HEADERS, params=params, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Request to search users failed: {e}"
        assert resp.status_code == 200, f"Expected 200 from GET /api/usuarios?buscar=Bob, got {resp.status_code}, body: {resp.text}"
        search_body = resp.json()
        assert "usuarios" in search_body and isinstance(search_body["usuarios"], list), "Search response missing 'usuarios' list"
        search_users = search_body["usuarios"]
        # At least one returned and all returned items should contain 'Bob' in nombre or email (case-insensitive)
        assert len(search_users) >= 1, "Expected at least one user in search results for 'Bob'"
        for su in search_users:
            nombre = (su.get("nombre") or "").lower()
            email = (su.get("email") or "").lower()
            assert "bob" in nombre or "bob" in email, f"Search result does not match 'Bob': {su}"

        # 3) Filter by role (rol=usuario) - should only include users with role 'usuario'
        params = {"rol": "usuario"}
        try:
            resp = requests.get(f"{BASE_URL}/api/usuarios", headers=HEADERS, params=params, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Request to filter users by role failed: {e}"
        assert resp.status_code == 200, f"Expected 200 from GET /api/usuarios?rol=usuario, got {resp.status_code}, body: {resp.text}"
        role_body = resp.json()
        assert "usuarios" in role_body and isinstance(role_body["usuarios"], list), "Role filter response missing 'usuarios' list"
        role_users = role_body["usuarios"]
        # All returned users should have rol == 'usuario'
        for ru in role_users:
            ru_rol = (ru.get("rol") or "").lower()
            assert ru_rol == "usuario", f"Expected role 'usuario' in result but got '{ru_rol}' for user {ru}"

        # 4) Pagination: request pagina=1 & limite=2
        params = {"pagina": 1, "limite": 2}
        try:
            resp = requests.get(f"{BASE_URL}/api/usuarios", headers=HEADERS, params=params, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Request to paginate users failed: {e}"
        assert resp.status_code == 200, f"Expected 200 from GET /api/usuarios?pagina=1&limite=2, got {resp.status_code}, body: {resp.text}"
        page_body = resp.json()
        assert page_body.get("pagina") == 1, f"Expected pagina==1, got {page_body.get('pagina')}"
        assert page_body.get("limite") == 2, f"Expected limite==2, got {page_body.get('limite')}"
        assert isinstance(page_body.get("usuarios"), list), "Paginated response 'usuarios' is not a list"
        # Number of returned usuarios should be <= limite
        assert len(page_body["usuarios"]) <= 2, f"Paginated usuarios length {len(page_body['usuarios'])} exceeds limite 2"

    finally:
        # Clean up created users using DELETE (logical delete)
        for uid in created_user_ids:
            try:
                resp = requests.delete(f"{BASE_URL}/api/usuarios/{uid}", headers=HEADERS, timeout=TIMEOUT)
            except requests.RequestException:
                # If deletion request fails, continue to attempt deleting others
                continue
            # Accept 200 for successful delete; if already deleted or not found might be 404 - ignore those in cleanup
            if resp.status_code not in (200, 404):
                # Not raising here to ensure cleanup attempts continue for others
                pass

if __name__ == "__main__":
    try:
        test_tc006_list_users_admin()
        print("TC006 passed")
    except AssertionError as e:
        print(f"TC006 failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"TC006 encountered an unexpected error: {e}", file=sys.stderr)
        sys.exit(2)
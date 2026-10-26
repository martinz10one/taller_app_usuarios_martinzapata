import requests
import uuid
import time
import sys
import traceback

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "x-token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}
TIMEOUT = 30


def _extract_user_id(user_obj):
    # user_obj might contain different id keys; try common ones
    for key in ("_id", "id", "uid"):
        if key in user_obj:
            return user_obj[key]
    return None


def test_get_usuarios_admin_list():
    unique_tag = f"tc006-{uuid.uuid4().hex[:8]}"
    created_users = []

    try:
        # Create two test users with predictable names to assert ordering & filtering
        users_to_create = [
            {"nombre": f"{unique_tag}-A", "email": f"{unique_tag}-a@example.com", "password": "P4sswordTest!", "rol": "usuario"},
            {"nombre": f"{unique_tag}-B", "email": f"{unique_tag}-b@example.com", "password": "P4sswordTest!", "rol": "usuario"},
        ]

        for u in users_to_create:
            resp = requests.post(f"{BASE_URL}/api/usuarios", headers=HEADERS, json=u, timeout=TIMEOUT)
            assert resp.status_code == 201, f"Expected 201 creating user, got {resp.status_code}, body: {resp.text}"
            body = resp.json()
            # response might be the user object directly or wrapped
            user_obj = body.get("usuario") if isinstance(body, dict) and "usuario" in body else body
            uid = _extract_user_id(user_obj)
            assert uid is not None, f"Created user has no id in response: {body}"
            created_users.append(uid)

        # Small pause to let DB indexes propagate if needed
        time.sleep(0.5)

        # Define a helper to perform the search + pagination GET
        def get_search(pagina=1, limite=10):
            params = {
                "buscar": unique_tag,
                "pagina": pagina,
                "limite": limite
            }
            r = requests.get(f"{BASE_URL}/api/usuarios", headers=HEADERS, params=params, timeout=TIMEOUT)
            return r

        # First execution: perform paginated GET requests and validations
        resp1_page1 = get_search(pagina=1, limite=1)
        assert resp1_page1.status_code == 200, f"Expected 200 on first page GET, got {resp1_page1.status_code}, body: {resp1_page1.text}"
        data1_p1 = resp1_page1.json()
        # Validate structure
        for key in ("total", "pagina", "limite", "totalPaginas", "usuarios"):
            assert key in data1_p1, f"Missing key '{key}' in response: {data1_p1}"
        assert isinstance(data1_p1["usuarios"], list), "usuarios should be a list"
        assert data1_p1["limite"] == 1, "limite should match requested value"
        assert data1_p1["pagina"] == 1, "pagina should be 1"

        # First execution: get page 2
        resp1_page2 = get_search(pagina=2, limite=1)
        assert resp1_page2.status_code == 200, f"Expected 200 on second page GET, got {resp1_page2.status_code}, body: {resp1_page2.text}"
        data1_p2 = resp1_page2.json()
        assert data1_p2["pagina"] == 2, "pagina should be 2 for second page"
        assert len(data1_p1["usuarios"]) == 1 and len(data1_p2["usuarios"]) == 1, "Each page should return one user for limite=1"

        # Validate ordering across pages: names should be ascending (A then B)
        name_page1 = data1_p1["usuarios"][0].get("nombre") or data1_p1["usuarios"][0].get("name")
        name_page2 = data1_p2["usuarios"][0].get("nombre") or data1_p2["usuarios"][0].get("name")
        assert name_page1 is not None and name_page2 is not None, "User objects must include a nombre field"
        assert name_page1 < name_page2, f"Expected page1 name < page2 name for ascending order, got '{name_page1}' >= '{name_page2}'"

        # Also fetch without pagination to get all matches and verify ordering
        resp_all = requests.get(f"{BASE_URL}/api/usuarios", headers=HEADERS, params={"buscar": unique_tag, "limite": 50, "pagina": 1}, timeout=TIMEOUT)
        assert resp_all.status_code == 200, f"Expected 200 on full GET, got {resp_all.status_code}, body: {resp_all.text}"
        data_all = resp_all.json()
        usuarios = data_all.get("usuarios")
        assert isinstance(usuarios, list), "usuarios should be list in full response"
        # Filter returned usuarios to those that exactly match our unique_tag prefix (defensive)
        filtered = [u for u in usuarios if (u.get("nombre") or "").startswith(unique_tag)]
        assert len(filtered) >= 2, f"Expected at least 2 created users in search results, found {len(filtered)}"
        names = [u.get("nombre") for u in filtered]
        assert names == sorted(names), f"Expected usuarios ordered by nombre ascending, got {names}"

        # Role filter: ensure filtering by rol returns only 'usuario' (we created usuario users)
        resp_role = requests.get(f"{BASE_URL}/api/usuarios", headers=HEADERS, params={"buscar": unique_tag, "rol": "usuario"}, timeout=TIMEOUT)
        assert resp_role.status_code == 200, f"Expected 200 on role-filtered GET, got {resp_role.status_code}, body: {resp_role.text}"
        data_role = resp_role.json()
        for u in data_role.get("usuarios", []):
            rol = u.get("rol")
            assert rol == "usuario", f"Expected rol 'usuario' in role-filtered results, got '{rol}'"

        # Second execution: repeat key GETs to confirm stability and identical content
        resp2_page1 = get_search(pagina=1, limite=1)
        assert resp2_page1.status_code == 200, f"Expected 200 on second execution page1 GET, got {resp2_page1.status_code}, body: {resp2_page1.text}"
        data2_p1 = resp2_page1.json()
        resp2_page2 = get_search(pagina=2, limite=1)
        assert resp2_page2.status_code == 200, f"Expected 200 on second execution page2 GET, got {resp2_page2.status_code}, body: {resp2_page2.text}"
        data2_p2 = resp2_page2.json()

        # Compare first and second execution results for the same pages
        assert data1_p1.get("usuarios") == data2_p1.get("usuarios"), "Page1 results differ between executions"
        assert data1_p2.get("usuarios") == data2_p2.get("usuarios"), "Page2 results differ between executions"
        # Also compare totals and pagination metadata
        for meta_key in ("total", "limite", "totalPaginas"):
            assert data1_p1.get(meta_key) == data2_p1.get(meta_key), f"Metadata '{meta_key}' differs between executions"

        print("TC006 passed: admin list users with search, role filter, pagination, ordering and stability confirmed.")

    except Exception:
        traceback.print_exc()
        raise
    finally:
        # Cleanup created users
        for uid in created_users:
            try:
                del_resp = requests.delete(f"{BASE_URL}/api/usuarios/{uid}", headers=HEADERS, timeout=TIMEOUT)
                # Accept 200 or 404 (if already removed) but log assertion if unexpected
                if del_resp.status_code not in (200, 404):
                    print(f"Warning: deleting user {uid} returned status {del_resp.status_code}, body: {del_resp.text}", file=sys.stderr)
            except Exception as e:
                print(f"Error deleting user {uid}: {e}", file=sys.stderr)


if __name__ == "__main__":
    test_get_usuarios_admin_list()
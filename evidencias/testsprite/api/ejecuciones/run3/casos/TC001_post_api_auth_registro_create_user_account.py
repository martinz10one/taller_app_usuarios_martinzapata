import requests
import uuid
import sys

BASE_ENDPOINT = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"

def test_post_api_auth_registro_create_user_account_tc001():
    url = f"{BASE_ENDPOINT}/api/auth/registro"
    unique = uuid.uuid4().hex[:8]
    nombre = f"TestUser {unique}"
    email = f"testuser_{unique}@example.com"
    password = "ValidPass1"  # meets 8-64, has uppercase, lowercase and number

    payload = {
        "nombre": nombre,
        "email": email,
        "password": password
    }
    headers = {"Content-Type": "application/json"}
    created_id = None

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        assert resp.status_code == 201, f"Expected 201 Created, got {resp.status_code}. Body: {resp.text}"

        try:
            data = resp.json()
        except ValueError:
            raise AssertionError(f"Response is not valid JSON. Body: {resp.text}")

        assert isinstance(data, dict), f"Response JSON is not an object: {data}"
        assert "token" in data and isinstance(data["token"], str) and data["token"], "Missing or invalid token in response"
        assert "usuario" in data and isinstance(data["usuario"], dict), "Missing usuario object in response"

        usuario = data["usuario"]
        # Ensure password is not present in returned usuario object
        assert "password" not in usuario, f"Usuario object should not include 'password'. Found: {usuario.get('password')}"

        # Ensure nombre and email match what was sent
        assert usuario.get("nombre") == nombre, f"Usuario.nombre mismatch: expected '{nombre}', got '{usuario.get('nombre')}'"
        assert usuario.get("email") == email, f"Usuario.email mismatch: expected '{email}', got '{usuario.get('email')}'"

        # Extract created user id from common fields
        created_id = usuario.get("uid") or usuario.get("id") or usuario.get("_id")
        assert created_id is not None, f"Created usuario id not found in response usuario: {usuario}"

    except requests.RequestException as e:
        raise AssertionError(f"HTTP request failed: {e}")

    finally:
        # Cleanup: attempt to delete created user using admin token
        if created_id:
            try:
                del_url = f"{BASE_ENDPOINT}/api/usuarios/{created_id}"
                del_headers = {"x-token": ADMIN_TOKEN}
                del_resp = requests.delete(del_url, headers=del_headers, timeout=30)
                # Accept 200 (deleted) or 404 (not found/already deleted) as acceptable cleanup outcomes
                if del_resp.status_code not in (200, 404):
                    raise AssertionError(f"Failed to delete test user {created_id}. Status: {del_resp.status_code}. Body: {del_resp.text}")
            except requests.RequestException as e:
                print(f"Cleanup request failed for user {created_id}: {e}", file=sys.stderr)
        else:
            # Fallback: try to locate user by email and delete if found
            try:
                search_url = f"{BASE_ENDPOINT}/api/usuarios"
                params = {"buscar": email}
                search_headers = {"x-token": ADMIN_TOKEN}
                search_resp = requests.get(search_url, headers=search_headers, params=params, timeout=30)
                if search_resp.status_code == 200:
                    try:
                        sdata = search_resp.json()
                    except ValueError:
                        sdata = {}
                    usuarios = sdata.get("usuarios") or []
                    for u in usuarios:
                        if u.get("email") == email:
                            uid = u.get("uid") or u.get("id") or u.get("_id")
                            if uid:
                                try:
                                    requests.delete(f"{BASE_ENDPOINT}/api/usuarios/{uid}", headers={"x-token": ADMIN_TOKEN}, timeout=30)
                                except requests.RequestException:
                                    pass
                                break
            except requests.RequestException:
                pass

if __name__ == "__main__":
    test_post_api_auth_registro_create_user_account_tc001()
    print("TC001 passed.")
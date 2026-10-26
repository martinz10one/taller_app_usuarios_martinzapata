import requests
import uuid
import sys
import time

BASE_URL = "http://localhost:3000"
ADMIN_TOKEN = "<ADMIN_JWT_REDACTED>"
TIMEOUT = 30


def test_put_api_auth_perfil_update_authenticated_user_profile():
    created_user_id = None
    user_token = None

    # Create a new user to act as the authenticated user for this test
    unique = uuid.uuid4().hex[:8]
    initial_nombre = f"TestUser {unique}"
    initial_email = f"testuser+{unique}@example.com"
    initial_password = "Str0ngPass1A"  # meets password rules: upper, lower, digit, length

    registro_url = f"{BASE_URL}/api/auth/registro"
    registro_payload = {
        "nombre": initial_nombre,
        "email": initial_email,
        "password": initial_password
    }
    try:
        r = requests.post(registro_url, json=registro_payload, headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Failed to call registro endpoint: {e}")

    if r.status_code != 201:
        # try to include response body for debugging
        body = None
        try:
            body = r.json()
        except Exception:
            body = r.text
        raise AssertionError(f"Expected 201 from registro, got {r.status_code}: {body}")

    try:
        registro_json = r.json()
    except Exception as e:
        raise AssertionError(f"registro response is not valid JSON: {e}")

    # Extract token and usuario
    if "token" not in registro_json:
        raise AssertionError(f"registro response missing token: {registro_json}")
    user_token = registro_json["token"]

    usuario_obj = registro_json.get("usuario")
    if not usuario_obj:
        # Some implementations might return the usuario directly
        # but PRD indicates { token, usuario }
        raise AssertionError(f"registro response missing usuario: {registro_json}")

    created_user_id = usuario_obj.get("_id") or usuario_obj.get("id") or usuario_obj.get("uid")
    if not created_user_id:
        # If no id found, still proceed but note we cannot cleanup later via admin delete
        created_user_id = None

    # Now perform the update of perfil with the user's token
    new_unique = uuid.uuid4().hex[:6]
    updated_nombre = initial_nombre + " Updated"
    updated_email = f"updated+{new_unique}@example.com"

    perfil_url = f"{BASE_URL}/api/auth/perfil"
    perfil_payload = {
        "nombre": updated_nombre,
        "email": updated_email
    }
    perfil_headers = {
        "Content-Type": "application/json",
        "x-token": user_token
    }

    try:
        r2 = requests.put(perfil_url, json=perfil_payload, headers=perfil_headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Failed to call PUT /api/auth/perfil: {e}")

    if r2.status_code != 200:
        body = None
        try:
            body = r2.json()
        except Exception:
            body = r2.text
        raise AssertionError(f"Expected 200 from PUT /api/auth/perfil, got {r2.status_code}: {body}")

    try:
        perfil_json = r2.json()
    except Exception as e:
        raise AssertionError(f"PUT /api/auth/perfil response is not valid JSON: {e}")

    # The response schema for PUT /api/auth/perfil is Usuario (might be directly the object or wrapped)
    if isinstance(perfil_json, dict) and ("usuario" in perfil_json):
        updated_usuario = perfil_json["usuario"]
    else:
        updated_usuario = perfil_json

    # Validate updated fields
    resp_nombre = updated_usuario.get("nombre")
    resp_email = updated_usuario.get("email")
    assert resp_nombre == updated_nombre, f"Expected nombre to be '{updated_nombre}', got '{resp_nombre}'"
    assert resp_email == updated_email, f"Expected email to be '{updated_email}', got '{resp_email}'"

    # Ensure password is not leaked in the response
    assert "password" not in updated_usuario, "Response must not contain password field"

    # Optionally verify profile via GET /api/auth/perfil with same user token
    try:
        r3 = requests.get(perfil_url, headers={"x-token": user_token}, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Failed to call GET /api/auth/perfil: {e}")

    if r3.status_code != 200:
        body = None
        try:
            body = r3.json()
        except Exception:
            body = r3.text
        raise AssertionError(f"Expected 200 from GET /api/auth/perfil, got {r3.status_code}: {body}")

    try:
        perfil_get_json = r3.json()
    except Exception as e:
        raise AssertionError(f"GET /api/auth/perfil response is not valid JSON: {e}")

    get_usuario = perfil_get_json if "usuario" not in perfil_get_json else perfil_get_json["usuario"]
    assert get_usuario.get("nombre") == updated_nombre, "GET perfil nombre does not match updated value"
    assert get_usuario.get("email") == updated_email, "GET perfil email does not match updated value"

    # If we reach here, the update succeeded
    print("Test TC004 passed: PUT /api/auth/perfil updated nombre and email successfully.")

    # Cleanup in finally block below
    try:
        pass
    finally:
        # Clean up created user via admin endpoint if we have its id
        if created_user_id:
            delete_url = f"{BASE_URL}/api/usuarios/{created_user_id}"
            delete_headers = {
                "x-token": ADMIN_TOKEN
            }
            try:
                rd = requests.delete(delete_url, headers=delete_headers, timeout=TIMEOUT)
            except requests.RequestException as e:
                print(f"Cleanup failed: could not call DELETE /api/usuarios/:id: {e}", file=sys.stderr)
                raise

            if rd.status_code not in (200, 404):
                body = None
                try:
                    body = rd.json()
                except Exception:
                    body = rd.text
                raise AssertionError(f"Cleanup DELETE expected 200 or 404, got {rd.status_code}: {body}")
            else:
                # Optionally print confirmation
                print(f"Cleanup: user {created_user_id} deletion response {rd.status_code}")


if __name__ == "__main__":
    test_put_api_auth_perfil_update_authenticated_user_profile()
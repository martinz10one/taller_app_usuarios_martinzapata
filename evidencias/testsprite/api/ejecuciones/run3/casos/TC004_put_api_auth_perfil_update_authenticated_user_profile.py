import requests
import time
import sys

BASE_URL = "http://localhost:3000"
TOKEN = "<ADMIN_JWT_REDACTED>"
HEADERS = {
    "x-token": TOKEN,
    "Content-Type": "application/json"
}
TIMEOUT = 30


def _extract_user(obj):
    # Response may be { usuario: {...} } or direct user object
    if isinstance(obj, dict):
        if "usuario" in obj and isinstance(obj["usuario"], dict):
            return obj["usuario"]
        # Some endpoints may return { token, usuario }
        if "token" in obj and "usuario" in obj and isinstance(obj["usuario"], dict):
            return obj["usuario"]
    return obj


def test_tc004_put_api_auth_perfil_update_authenticated_user_profile():
    perfil_url = f"{BASE_URL}/api/auth/perfil"

    # Step 1: Retrieve current profile
    try:
        resp = requests.get(perfil_url, headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Failed to GET perfil: {e}")

    assert resp.status_code == 200, f"Expected 200 from GET perfil, got {resp.status_code}: {resp.text}"
    try:
        resp_json = resp.json()
    except ValueError:
        raise AssertionError(f"GET perfil did not return JSON: {resp.text}")

    current_user = _extract_user(resp_json)
    assert isinstance(current_user, dict), f"Unexpected perfil payload: {resp_json}"
    original_nombre = current_user.get("nombre")
    original_email = current_user.get("email")
    assert original_nombre is not None and original_email is not None, "Perfil missing nombre or email"

    # Prepare new unique values
    timestamp = int(time.time())
    new_nombre = f"{original_nombre} Updated {timestamp}"
    new_email = f"test+{timestamp}@example.com"

    update_payload = {"nombre": new_nombre, "email": new_email}

    # Perform update and ensure revert in finally
    try:
        try:
            put_resp = requests.put(perfil_url, headers=HEADERS, json=update_payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Failed to PUT perfil: {e}")

        assert put_resp.status_code == 200, f"Expected 200 from PUT perfil, got {put_resp.status_code}: {put_resp.text}"
        try:
            put_json = put_resp.json()
        except ValueError:
            raise AssertionError(f"PUT perfil did not return JSON: {put_resp.text}")

        updated_user = _extract_user(put_json)
        assert isinstance(updated_user, dict), f"Unexpected PUT perfil payload: {put_json}"
        assert updated_user.get("nombre") == new_nombre, f"Nombre was not updated. Expected '{new_nombre}', got '{updated_user.get('nombre')}'"
        assert updated_user.get("email") == new_email, f"Email was not updated. Expected '{new_email}', got '{updated_user.get('email')}'"

    finally:
        # Revert to original values to avoid side effects
        revert_payload = {"nombre": original_nombre, "email": original_email}
        try:
            revert_resp = requests.put(perfil_url, headers=HEADERS, json=revert_payload, timeout=TIMEOUT)
            # Accept either 200 or 400 (in case original email is no longer valid); assert 200 ideally
            if revert_resp.status_code != 200:
                # Try to surface the revert failure but do not mask original assertion
                try:
                    body = revert_resp.json()
                except ValueError:
                    body = revert_resp.text
                raise AssertionError(f"Failed to revert perfil. Status {revert_resp.status_code}: {body}")
        except requests.RequestException as e:
            raise AssertionError(f"Failed to revert perfil due to request error: {e}")


if __name__ == "__main__":
    try:
        test_tc004_put_api_auth_perfil_update_authenticated_user_profile()
        print("TC004 passed")
    except AssertionError as e:
        print(f"TC004 failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC004 unexpected error: {e}")
        sys.exit(1)
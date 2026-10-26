# TestSprite AI Testing Report (MCP) — API

---

## 1️⃣ Document Metadata
- **Project Name:** api (App de usuarios — API REST)
- **Date:** 2026-10-26
- **Prepared by:** TestSprite AI Team; revisado y completado por Martin Zapata
- **Execution type:** backend, scope `codebase`
- **Local endpoint:** `http://localhost:3000`
- **Authentication:** API key header `x-token` con un JWT de administrador (caducidad 4 h)
- **PRD usado:** [`PRD.md`](../../../PRD.md)
- **Plan de pruebas:** [`plan/testsprite_backend_test_plan.json`](plan/testsprite_backend_test_plan.json)
- **Código analizado:** [`code_summary.yaml`](code_summary.yaml)

---

## 2️⃣ Requirement Validation Summary

### Requirement: Autenticación y perfil
- **Description:** Registro público, login, consulta del perfil, actualización de nombre/email y cambio de contraseña. El JWT viaja en el header `x-token`.

#### Test TC001 post api auth registro create user account
- **Test Code:** [TC001](ejecuciones/run3/casos/TC001_post_api_auth_registro_create_user_account.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/e29c9166-b4ea-4e0d-9cd3-f91a4b89dec6>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** El registro devuelve 201 con `token` y `usuario`, sin `password`. El rol queda forzado a `usuario`.

#### Test TC002 post api auth login authenticate user
- **Test Code:** [TC002](ejecuciones/run3/casos/TC002_post_api_auth_login_authenticate_user.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/8aef2e80-abae-4fbf-a50c-100d31003280>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Login correcto con 200, `token` y usuario con `uid`. No se expone el hash de la contraseña.

#### Test TC003 get api auth perfil get authenticated user profile
- **Test Code:** [TC003](ejecuciones/run3/casos/TC003_get_api_auth_perfil_get_authenticated_user_profile.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/50b640de-105c-4999-9316-3f71ec979308>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** `GET /api/auth/perfil` con `x-token` válido responde 200 con los datos del usuario autenticado.

#### Test TC004 put api auth perfil update authenticated user profile
- **Test Code:** [TC004](ejecuciones/run3/casos/TC004_put_api_auth_perfil_update_authenticated_user_profile.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/901db8d3-bdc0-4e50-bdee-7230178fb424>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** La actualización parcial de `nombre` y `email` responde 200 y conserva el mismo `uid`.

#### Test TC005 put api auth password change user password
- **Test Code:** [TC005](ejecuciones/run3/casos/TC005_put_api_auth_password_change_user_password.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/bc9df9b9-18be-4c50-8c98-75ffe05b5430>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** El cambio de contraseña responde 200, el login con la nueva contraseña funciona y el login con la anterior deja de funcionar.

---

### Requirement: Administración de usuarios
- **Description:** CRUD de usuarios restringido a administradores, con búsqueda, filtro por rol, paginación, reglas de auto-protección y borrado lógico.

#### Test TC006 get api usuarios list users with admin role
- **Test Code:** [TC006](ejecuciones/run3/casos/TC006_get_api_usuarios_list_users_with_admin_role.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/411af12e-c24d-4cba-b470-291c51c87782>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** El listado devuelve `total`, `pagina`, `limite`, `totalPaginas` y usuarios activos ordenados por nombre.

#### Test TC007 get api usuarios id get user details by id
- **Test Code:** [TC007](ejecuciones/run3/casos/TC007_get_api_usuarios_id_get_user_details_by_id.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/95b21e0c-91c8-4cd6-8b7c-17644296e71b>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** `GET /api/usuarios/:id` con id válido devuelve 200 y el usuario solicitado.

#### Test TC008 post api usuarios create new user by admin
- **Test Code:** [TC008](ejecuciones/run3/casos/TC008_post_api_usuarios_create_new_user_by_admin.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/b37bf8c0-9210-4c1c-96dc-5282fe1b5c37>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** El admin crea un usuario con 201; la contraseña se guarda hasheada y nunca se devuelve.

#### Test TC009 put api usuarios id update user details by admin
- **Test Code:** [TC009](ejecuciones/run3/casos/TC009_put_api_usuarios_id_update_user_details_by_admin.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/05c52fc4-93ed-4427-ba0d-943f1f646ed0>
- **Status:** ✅ Passed (run 3)
- **Severity:** LOW
- **Analysis / Findings:** En la ejecución 2 este caso falló por un defecto del propio test generado: envió `rol: "admin"` al admin (mismo rol), por lo que el 200 era correcto. En la ejecución 3 se envió `rol: "usuario"` y la API respondió 400 `No puedes cambiar tu propio rol`. Comportamiento verificado también manualmente y con la prueba de integración [`api/tests/integration/usuarios.test.js`](../../../api/tests/integration/usuarios.test.js).

#### Test TC010 delete api usuarios id logical delete user by admin
- **Test Code:** [TC010](ejecuciones/run3/casos/TC010_delete_api_usuarios_id_logical_delete_user_by_admin.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/be361980-e9bf-4b5c-802a-620ab0523d93>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** El borrado lógico responde 200 con `mensaje: "Usuario eliminado"` y el usuario deja de estar activo.

---

## 3️⃣ Coverage & Matching Metrics

Ejecuciones realizadas:

| Ejecución | Motivo | Total | ✅ Passed | ❌ Failed | ⛔ Blocked |
|---|---|---:|---:|---:|---:|
| run1 | Primera ejecución | 10 | 10 | 0 | 0 |
| run2 | Segunda ejecución (estabilidad) | 10 | 9 | 1 | 0 |
| run3 | Repetición tras analizar el fallo de TC009 | 10 | 10 | 0 | 0 |

- **100 % de los casos del plan pasan en la ejecución final (run3).**
- Los 10 casos del plan cubren autenticación/perfil (5) y administración de usuarios (5).

| Requirement | Total Tests | ✅ Passed | ❌ Failed |
|---|---:|---:|---:|
| Autenticación y perfil | 5 | 5 | 0 |
| Administración de usuarios | 5 | 5 | 0 |
| **Total** | **10** | **10** | **0** |

Evidencias de cada ejecución en [`ejecuciones/`](ejecuciones/). Panel local de TestSprite en [`../paneles/api-final-run3-10-10.png`](../paneles/api-final-run3-10-10.png) y fallo de la ejecución 2 en [`../paneles/api-run2-9-10.png`](../paneles/api-run2-9-10.png).

---

## 4️⃣ Key Gaps / Risks

> **Cobertura del plan:** TestSprite generó 10 casos, centrados en caminos felices. No generó casos negativos de 401/403, ids mal formados, paginación fuera de rango, JSON inválido ni contraseñas débiles. Esos casos sí están cubiertos por las 80 pruebas de Vitest/Supertest del proyecto.
>
> **Dependencia de estado:** los casos usan datos creados y borrados contra una base MongoDB real (`app-usuarios-testsprite`). Un email de un usuario borrado lógicamente sigue reservado por el índice único; es el comportamiento esperado, pero obliga a usar emails nuevos en cada repetición.
>
> **Credenciales en el código generado:** TestSprite incrustó el JWT de administrador en los archivos Python. Las copias de evidencia están redactadas con `<ADMIN_JWT_REDACTED>`; la carpeta de trabajo `api/testsprite_tests/` está ignorada por Git.
>
> **Valor añadido:** la ejecución 2 detectó un falso positivo (TC009) que permitió revisar la regla de auto-cambio de rol y confirmar que la API responde 400 cuando realmente se intenta cambiar el rol. No se encontró ningún error real en la API.

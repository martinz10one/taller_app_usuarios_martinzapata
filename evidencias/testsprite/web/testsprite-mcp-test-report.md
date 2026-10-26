# TestSprite AI Testing Report (MCP) — Web

---

## 1️⃣ Document Metadata
- **Project Name:** web (App de usuarios — frontend Vue 3)
- **Date:** 2026-10-26
- **Prepared by:** TestSprite AI Team; revisado y completado por Martin Zapata
- **Execution type:** frontend, scope `codebase`
- **Local endpoint:** `http://localhost:5173`
- **Credenciales de prueba:** `admin@demo.com` / `Admin123!`
- **PRD usado:** [`PRD.md`](../../../PRD.md)
- **Plan de pruebas:** [`plan/testsprite_frontend_test_plan.json`](plan/testsprite_frontend_test_plan.json)
- **Código analizado:** [`code_summary.yaml`](code_summary.yaml)

---

## 2️⃣ Requirement Validation Summary

### Requirement: Autenticación, registro y sesión
- **Description:** Login de administrador y de usuario normal, registro público, cierre de sesión y redirección según el rol.

#### Test TC001 Iniciar sesión como administrador
- **Test Code:** [TC001](ejecuciones/run2/casos/TC001_Iniciar_sesin_como_administrador.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/28ffb424-be38-4a95-ac0d-26d934d63426>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Con `admin@demo.com` se entra al panel `/usuarios` y se ve la tabla de usuarios. En la ejecución 1 este caso quedó bloqueado por la inestabilidad del servidor de desarrollo; en producción pasó.

#### Test TC002 Registrar una cuenta nueva y acceder al destino correcto
- **Test Code:** [TC002](ejecuciones/run3/casos/TC002_Registrar_una_cuenta_nueva_y_acceder_al_destino_correcto.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/77edc857-ee32-4f9e-945f-61b5bb2864b0>
- **Status:** ✅ Passed (run 3)
- **Severity:** LOW
- **Analysis / Findings:** La ejecución 2 falló porque reutilizó `qa.visitante.20261026@example.com`, ya registrado y borrado lógicamente en la ejecución 1, y después de ver el aviso de email duplicado cambió el correo pero no volvió a pulsar «Crear cuenta». En la ejecución 3, con un email nuevo y reenviando el formulario, el registro pasó y redirigió a `/perfil`.

#### Test TC003 Crear cuenta y entrar al perfil
- **Test Code:** [TC003](ejecuciones/run2/casos/TC003_Crear_cuenta_y_entrar_al_perfil.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/92e96f11-a8e6-485f-9fb8-f9e86cb72a9b>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Tras crear la cuenta se muestran los datos del perfil y el rol `Usuario`.

#### Test TC004 Iniciar sesión como usuario normal
- **Test Code:** [TC004](ejecuciones/run2/casos/TC004_Iniciar_sesin_como_usuario_normal.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/dcceb6ca-b0a8-434a-bc0f-a053904ead06>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** El usuario normal entra a `/perfil` y no ve el enlace de administración.

#### Test TC005 Cerrar sesión y volver al acceso público
- **Test Code:** [TC005](ejecuciones/run2/casos/TC005_Cerrar_sesin_y_volver_al_acceso_pblico.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/bff707e6-c223-4132-8a58-e5f0f0965e5f>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** «Cerrar sesión» elimina la sesión y deja al visitante en `/login`; una ruta protegida vuelve a pedir autenticación.

#### Test TC007 Redirigir a la vista correcta según el rol al entrar
- **Test Code:** [TC007](ejecuciones/run2/casos/TC007_Redirigir_a_la_vista_correcta_segn_el_rol_al_entrar.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/a98a6a69-2baa-4e62-8885-e680f5524de5>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** `/` redirige a `/usuarios` para admin y a `/perfil` para usuario.

---

### Requirement: Control de acceso por rol
- **Description:** Las rutas de administración están protegidas por la guarda `requiresAdmin`; sin sesión se redirige a login.

#### Test TC006 Bloquear acceso a usuarios para un usuario normal
- **Test Code:** [TC006](ejecuciones/run2/casos/TC006_Bloquear_acceso_a_usuarios_para_un_usuario_normal.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/50bbb6f9-3ac8-45a8-bc26-eb03c3c3b774>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Un usuario autenticado sin rol admin que abre `/usuarios` termina en `/perfil`.

#### Test TC012 Bloquear el acceso a usuarios sin permisos
- **Test Code:** [TC012](ejecuciones/run2/casos/TC012_Bloquear_el_acceso_a_usuarios_sin_permisos.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/c9b04b9b-f895-4980-bf44-fc3304f3d54b>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Sin sesión, `/usuarios` redirige a `/login` y no se muestra contenido administrativo.

---

### Requirement: Gestión de usuarios (admin)
- **Description:** Crear, editar, eliminar con confirmación, buscar y filtrar usuarios desde el panel de administración.

#### Test TC008 Eliminar lógicamente un usuario con confirmación
- **Test Code:** [TC008](ejecuciones/run2/casos/TC008_Eliminar_lgicamente_un_usuario_con_confirmacin.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/4dc1b414-93c0-45cf-9540-bd7fef8d7c52>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** El diálogo de confirmación elimina al usuario y la fila desaparece del listado.

#### Test TC009 Crear un usuario nuevo desde el panel de administración
- **Test Code:** [TC009](ejecuciones/run2/casos/TC009_Crear_un_usuario_nuevo_desde_el_panel_de_administracin.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/c8ee0b15-f7dc-443c-a202-1f7461ea4153>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** El formulario valida los campos, crea el usuario y lo muestra en la tabla.

#### Test TC010 Editar un usuario existente desde el panel de administración
- **Test Code:** [TC010](ejecuciones/run2/casos/TC010_Editar_un_usuario_existente_desde_el_panel_de_administracin.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/22d939e7-f13e-4113-a080-437628e82e4d>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Los cambios de nombre/email se guardan y se reflejan en la tabla.

#### Test TC011 Editar un usuario existente
- **Test Code:** [TC011](ejecuciones/run2/casos/TC011_Editar_un_usuario_existente.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/e630cdfa-2e4a-488b-a399-c704331372ab>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** Caso duplicado del anterior generado por TestSprite; también pasa y confirma la persistencia.

#### Test TC013 Buscar usuarios en el listado
- **Test Code:** [TC013](ejecuciones/run2/casos/TC013_Buscar_usuarios_en_el_listado.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/060e4708-fd0c-49be-a135-548a71a68009>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** El buscador filtra por nombre/email y el contador de resultados cambia.

#### Test TC014 Buscar y filtrar usuarios desde el panel de administración
- **Test Code:** [TC014](ejecuciones/run2/casos/TC014_Buscar_y_filtrar_usuarios_desde_el_panel_de_administracin.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/3ffc1797-8e0b-4f79-bbda-dcc336acfabc>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** La combinación de búsqueda y filtro por rol devuelve solo las filas esperadas.

#### Test TC015 Filtrar usuarios por rol
- **Test Code:** [TC015](ejecuciones/run2/casos/TC015_Filtrar_usuarios_por_rol.py)
- **Test Visualization and Result:** <https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/06da11ab-ef85-43a0-9a4e-08fa11d8a0e4>
- **Status:** ✅ Passed
- **Severity:** LOW
- **Analysis / Findings:** El filtro `admin`/`usuario` reduce el listado correctamente.

---

## 3️⃣ Coverage & Matching Metrics

Ejecuciones realizadas:

| Ejecución | Entorno | Seleccionados | ✅ Passed | ❌ Failed | ⛔ Blocked |
|---|---|---:|---:|---:|---:|
| run1 | `vite dev` en 5173 | 15 | 6 | 0 | 9 |
| run2 | `vite preview` (build de producción) en 5173 | 15 | 14 | 1 | 0 |
| run3 | `vite preview`, solo TC002 | 1 | 1 | 0 | 0 |

- **Ejecución 2: 14/15 (93,3 %).** El único fallo, TC002, se analizó y se resolvió en la ejecución dirigida 3.
- **Resultado final considerando run2 + run3: 15/15 casos ejecutados pasan.**
- La ejecución 1 quedó bloqueada por la inestabilidad del servidor de desarrollo de Vite bajo carga concurrente, no por un fallo funcional.

| Requirement | Total Tests | ✅ Passed | ❌ Failed |
|---|---:|---:|---:|
| Autenticación, registro y sesión | 6 | 6 | 0 |
| Control de acceso por rol | 2 | 2 | 0 |
| Gestión de usuarios (admin) | 7 | 7 | 0 |
| **Total** | **15** | **15** | **0** |

Evidencias en [`ejecuciones/`](ejecuciones/). Paneles locales de TestSprite: [`../paneles/web-run1-6-15.png`](../paneles/web-run1-6-15.png), [`../paneles/web-run2-14-15.png`](../paneles/web-run2-14-15.png) y [`../paneles/web-run3-tc002-1-1.png`](../paneles/web-run3-tc002-1-1.png).

---

## 4️⃣ Key Gaps / Risks

> **Casos no ejecutados:** el plan generado tiene 28 casos; TestSprite limitó la ejecución a 15 casos de prioridad alta. Los 13 restantes (perfil, cambio de contraseña, validaciones de confirmación, 404) están cubiertos por las 129 pruebas de Vitest y los 29 flujos de Playwright del proyecto, pero no por esta ejecución de TestSprite.
>
> **Entorno:** `vite dev` no es adecuado para pruebas concurrentes de TestSprite: la ejecución 1 produjo 9 páginas en blanco. Se pasó a `vite preview` con build de producción y se añadió `preview.proxy` para `/api` en `web/vite.config.js`. Este fue el hallazgo de configuración más útil de TestSprite.
>
> **Datos compartidos:** los tests usan la base `app-usuarios-testsprite` y emails únicos. Un email de una cuenta borrada lógicamente sigue reservado por el índice único; la ejecución 2 reutilizó uno y provocó un falso fallo en TC002.
>
> **Duplicados del plan:** TestSprite generó casos repetidos (TC010/TC011, TC013/TC014) y varios casos de perfil/contraseña que no llegaron a ejecutarse. No se modificaron las pruebas manuales para “hacerlas pasar”.
>
> **Valor añadido:** la ejecución en navegador real validó login, registro, guards, CRUD, búsqueda, filtro y borrado sin mocks, y descubrió que el preview de producción necesitaba proxy hacia la API.

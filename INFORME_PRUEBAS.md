# Informe de pruebas — App de usuarios

**Proyecto:** API REST + web de gestión de usuarios
**Repositorio:** `taller_app_usuarios_martinzapata`
**Fecha de ejecución:** 26 de octubre de 2026
**Entorno:** Node.js 23.8.0, npm 10.9.2, MongoDB local, Linux

## 1. Resumen ejecutivo

Se automatizaron las pruebas de la API y de la web con Vitest, Supertest, Vue Test Utils y Playwright. Todas las suites pasan y los umbrales de cobertura se cumplen en ambos proyectos. También se añadieron pruebas de accesibilidad con Axe y se corrigieron dos problemas reales de la interfaz detectados por ellas.

TestSprite se ejecutó sobre la API y sobre la web con el PRD del proyecto. La API terminó 10/10 y la web 15/15 (14/15 en la segunda ejecución más la repetición dirigida del único fallo). Los fallos intermedios se analizaron y resultaron ser defectos de los tests generados o del entorno, no de la aplicación; el hallazgo más útil fue que el preview de producción no tenía proxy hacia la API, lo que se corrigió en `web/vite.config.js`.

| Proyecto / tipo | Herramienta | Archivos | Pruebas | Pasan | Fallan | Cobertura de líneas |
| --- | --- | --- | --- | --- | --- | --- |
| API — unitarias e integración | Vitest + Supertest + `mongodb-memory-server` | 9 | 80 | 80 | 0 | 95,02 % |
| Web — unitarias, componentes y router | Vitest + Vue Test Utils + jsdom | 18 | 129 | 129 | 0 | 100 % |
| Web + API — end-to-end | Playwright (Chromium y Firefox) | 5 specs | 29 ejecuciones | 29 | 0 | No aplica |
| API — TestSprite | TestSprite MCP | 10 casos | 10 | 10 | 0 | No aplica |
| Web — TestSprite | TestSprite MCP | 15 casos ejecutados de 28 planificados | 15 | 15 | 0 | No aplica |

> Las 29 ejecuciones de Playwright incluyen el proyecto `setup` que guarda la sesión del administrador y 14 pruebas por cada uno de los dos navegadores.
>
> En TestSprite web, la segunda ejecución terminó 14/15 y el caso TC002 se repitió de forma dirigida en una tercera ejecución (1/1). El resultado final de los 15 casos ejecutados es 15/15; el detalle está en la sección 7.

## 2. Entorno y comandos

```bash
# API
cd api
npm test
npm run coverage

# Web
cd web
npm test
npm run coverage
npx playwright install chromium firefox
npm run test:e2e
```

- Las pruebas de la API usan MongoDB en memoria (`mongodb-memory-server`), por lo que no requieren MongoDB instalado ni tocan la base de desarrollo.
- Las pruebas E2E usan la base `app-usuarios-e2e` porque `npm run seed` borra la colección.
- Las pruebas de la web limpian `localStorage` y restauran los mocks antes de cada caso.
- No hay pruebas marcadas con `.skip` ni `.only`; ninguna depende del orden de ejecución.

## 3. Pruebas de la API

### 3.1 Pruebas unitarias

| Archivo | Qué verifica |
| --- | --- |
| `tests/unit/validar-rol.test.js` | 500 sin `req.usuario`, 403 con rol no permitido, `next()` con rol permitido y varios roles. |
| `tests/unit/validar-jwt.test.js` | 401 sin token, token inválido, token con otro secreto, usuario desactivado o inexistente; usuario válido en `req` y `next()`. |
| `tests/unit/validar-campos.test.js` | 400 con `{ path, msg }` sin filtrar el valor y paso al controlador sin errores. |
| `tests/unit/generar-jwt.test.js` | El token contiene `uid` y `rol`, y expira correctamente. |
| `tests/unit/db-validators.test.js` | Roles válidos, email duplicado, email propio al editar y normalización de mayúsculas/espacios. |
| `tests/unit/modelo-usuario.test.js` | Hash con bcrypt, `validarPassword()`, `toJSON()` sin `password`/`_id` y valores por defecto. |

### 3.2 Pruebas de integración

| Archivo | Qué verifica |
| --- | --- |
| `tests/integration/auth.test.js` | Registro, login, perfil, actualización de perfil y cambio de contraseña, incluidos todos los errores 400/401. |
| `tests/integration/usuarios.test.js` | Autenticación y autorización (401/403), listado, paginación, búsqueda, filtro por rol, CRUD, borrado lógico y reglas del administrador. |
| `tests/integration/misc.test.js` | `GET /api/health`, 404 en JSON, JSON mal formado y errores de persistencia (email duplicado, `ValidationError` y error inesperado 500). |

Casos destacados:

- Registro con `rol: "admin"` en el cuerpo → se crea como `usuario`.
- Login con contraseña incorrecta y con email inexistente → mismo mensaje `Credenciales inválidas`.
- Usuario desactivado → `401 Usuario desactivado` y no aparece en el listado.
- Búsqueda literal de caracteres especiales (`(especial)`) sin interpretarlos como expresión regular.
- El administrador no puede cambiar su propio rol ni eliminarse a sí mismo.
- Eliminar un usuario es un borrado lógico: desaparece del listado y ya no puede iniciar sesión.

## 4. Pruebas de la web

### 4.1 Unitarias y de componentes

| Área | Archivos | Qué verifica |
| --- | --- | --- |
| Utilidades | `validators.test.js` | Nombre, email, contraseña (longitud, mayúscula, minúscula, número), confirmación e `isValid`. |
| Servicios | `http.test.js`, `services.test.js` | Header `x-token`, serialización JSON, query string, `ApiError`, 401 y `setUnauthorizedHandler`; rutas y métodos de `authApi` y `usersApi`. |
| Composables | `useAuth.test.js`, `useToast.test.js` | Login, registro, logout, restauración de sesión, rol y temporizadores de los toasts. |
| Componentes | `FormField`, `PaginationBar`, `ConfirmDialog`, `AlertMessage`, `AppHeader`, `ToastContainer` | Errores por campo, mostrar/ocultar contraseña, paginación, confirmación, toasts y navegación. |
| Vistas | `LoginView`, `RegisterView`, `ProfileView`, `UserFormView`, `UsersView`, `NotFoundView` | Validación local, errores de la API, creación/edición, búsqueda con debounce, filtros, paginación y eliminación con confirmación. |
| Router | `router.test.js` | Guardas `requiresAuth`, `guestOnly`, `requiresAdmin`, redirección por rol y título del documento. |

### 4.2 End-to-end con Playwright

| Flujo | Chromium | Firefox |
| --- | --- | --- |
| Login incorrecto y registro de cuenta | Sí | Sí |
| Redirección por sesión y por rol | Sí | Sí |
| CRUD del administrador con búsqueda y edición | Sí | Sí |
| Eliminación con diálogo y bloqueo del login | Sí | Sí |
| Filtro por rol y paginación | Sí | Sí |
| Cambio de contraseña y login con la nueva | Sí | Sí |
| Restauración de sesión al recargar | Sí | Sí |
| Página 404 | Sí | Sí |
| Accesibilidad (login y listado) | Sí | Sí |

La sesión del administrador se reutiliza mediante `storageState` (`web/e2e/.auth/admin.json`), generado una sola vez por el proyecto `setup`. Los flujos de invitado limpian ese estado explícitamente.

## 5. Cobertura

Umbrales configurados: 80 % de líneas, funciones y sentencias; 70 % de ramas. `npm run coverage` falla si no se cumplen.

| Proyecto | Sentencias | Ramas | Funciones | Líneas | Resultado |
| --- | --- | --- | --- | --- | --- |
| API | 95,02 % | 89,10 % | 100 % | 95,02 % | Cumple |
| Web | 100 % | 95,64 % | 93,81 % | 100 % | Cumple |

### 5.1 Líneas sin cubrir y pruebas agregadas

En el reporte HTML de la API, `app.js` aparecía inicialmente con 55,88 % de líneas. Las líneas 17–22 corresponden al logger de peticiones, que se desactiva intencionalmente cuando `NODE_ENV === "test"` para no inundar la salida. Las líneas 46–56 eran las ramas de error del middleware: email duplicado (`code 11000`), `ValidationError` de Mongoose y error inesperado 500. Se agregaron tres pruebas en `tests/integration/misc.test.js` que simulan esos fallos con `vi.spyOn(Usuario.prototype, "save")`; con ellas `app.js` subió a 82,35 % y el total de la API a 95,02 %. La única parte sin cubrir de `app.js` es el logger, cubierto por diseño fuera de las pruebas.

Los bloques `catch` de `controllers/auth.js` y `controllers/usuarios.js` (errores inesperados de base de datos en registro, actualización, cambio de contraseña y borrado) siguen sin ejecutarse porque requieren simular fallos de MongoDB en cada controlador. No son requisito del taller y su ausencia no impide cumplir los umbrales.

En la web se alcanzó el 100 % de líneas y sentencias. Las ramas y funciones restantes corresponden a caminos defensivos o variantes de plantilla:

- `FormField.vue` (87,5 % de ramas): combinaciones de `type`, `hint` y `error` que no cambian el comportamiento probado.
- `router/index.js` (85,71 % de ramas, 62,5 % de funciones): funciones flecha de redirección y la rama sin `title`.
- `ProfileView.vue`, `UserFormView.vue` y `UsersView.vue`: valores por defecto (`??`, `?.`) y ramas de plantilla para roles/fechas.

Se agregaron pruebas para las ramas de comportamiento relevantes que faltaban:

- `services.test.js`: cubre al 100 % `authApi.js` y `usersApi.js`, que antes aparecían con 0 % de funciones porque las vistas los mockeaban.
- `UsersView`: retroceso automático cuando la última página queda vacía y toast de error cuando falla la eliminación.
- `ProfileView`: error general al guardar el perfil sin detalles por campo.
- `UserFormView`: error general al cargar un usuario con un fallo 500.

## 6. Hallazgos y decisiones

| # | Hallazgo | Cómo se detectó | Causa | Decisión |
| --- | --- | --- | --- | --- |
| 1 | Los enlaces del login no se distinguían del texto por color (contraste 1,3:1) y algunos textos tenían 4,47:1. | Axe en Playwright (`link-in-text-block` y `color-contrast`). | `text-decoration: none` en enlaces y un gris demasiado claro para texto pequeño. | Se subrayaron los enlaces y se cambió `--color-text-muted` a `#4b5563`; no se relajaron las aserciones. |
| 2 | La prueba de recarga de sesión fallaba de forma intermitente en Firefox. | Playwright, proyecto Firefox. | La recarga ocurría antes de que la vista terminara de cargar; el token sí se conservaba y `/api/auth/perfil` respondía 200. | Se espera a que la tabla tenga filas y el encabezado muestre el usuario antes de recargar; se eliminó la instrumentación temporal. |
| 3 | La aserción del toast de contraseña fallaba por modo estricto. | Playwright, flujo de cambio de contraseña. | Había más de un toast visible en ese momento. | Se filtra por el texto `Contraseña actualizada` en lugar de asumir un único toast. |
| 4 | Vitest intentaba ejecutar los specs de Playwright y fallaba al recolectarlos. | `npm test` en web tras crear `e2e/`. | El patrón por defecto de Vitest incluye `*.spec.js`. | Se declaró `include: ["tests/**/*.test.js"]` en `web/vitest.config.js`. |
| 5 | La prueba de “colección vacía” de la API no era verificable. | `npm test` de la API. | Para pedir el listado hace falta un administrador, así que la colección nunca podía quedar vacía. | Se reemplazó por el caso realista “un solo usuario” y se mantuvo la verificación de `total`/`totalPaginas`. |
| 6 | La salida de `npm test` se llenaba de logs de peticiones. | Ejecución de la suite de la API. | El logger se registraba siempre. | Se silencia cuando `NODE_ENV === "test"`; en desarrollo sigue activo. |
| 7 | El build de producción servido con `vite preview` no podía hablar con la API. | TestSprite web, ejecución 1 con `vite dev` bloqueada y paso a producción. | `vite.config.js` solo definía `server.proxy`, no `preview.proxy`. | Se agregó `preview.proxy` para `/api`; el build de producción funciona en el puerto 5173. |

Los hallazgos 1, 2 y 7 son los más relevantes: el primero era un problema real de accesibilidad, el segundo una carrera de la prueba que ocultaba el comportamiento correcto de la aplicación y el séptimo una carencia real de configuración del despliegue de producción que descubrió TestSprite.

## 7. Pruebas con TestSprite

Se ejecutó el servidor MCP oficial de TestSprite (`@testsprite/testsprite-mcp@0.0.47`) con la API key fuera del repositorio, usando [`PRD.md`](PRD.md) y las cuentas del seed. La API se levantó en el puerto 3000 con la base `app-usuarios-testsprite` y la web en el 5173. La carpeta de trabajo `testsprite_tests/` está ignorada por Git; las copias de evidencia, con los JWT redactados, están en [`evidencias/testsprite/`](evidencias/testsprite/).

### 7.1 Ejecuciones de la API

| Ejecución | Motivo | Total | Pasan | Fallan | Bloqueados |
| --- | --- | --- | --- | --- | --- |
| run1 | Primera ejecución backend | 10 | 10 | 0 | 0 |
| run2 | Segunda ejecución (estabilidad) | 10 | 9 | 1 | 0 |
| run3 | Repetición tras analizar el fallo de TC009 | 10 | 10 | 0 | 0 |

El plan de la API tiene 10 casos: registro, login, perfil (consulta y edición), cambio de contraseña, listado, consulta por id, creación, edición y borrado lógico. La ejecución final pasó 10/10. Panel: [`evidencias/testsprite/paneles/api-final-run3-10-10.png`](evidencias/testsprite/paneles/api-final-run3-10-10.png).

### 7.2 Ejecuciones de la web

| Ejecución | Entorno | Seleccionados | Pasan | Fallan | Bloqueados |
| --- | --- | --- | --- | --- | --- |
| run1 | `vite dev` en 5173 | 15 | 6 | 0 | 9 |
| run2 | `vite preview` (build de producción) en 5173 | 15 | 14 | 1 | 0 |
| run3 | `vite preview`, solo TC002 | 1 | 1 | 0 | 0 |

El plan de la web tiene 28 casos; TestSprite ejecutó los 15 de prioridad alta. La segunda ejecución quedó 14/15 y el único fallo se repitió de forma dirigida en la tercera ejecución, que pasó. El resultado final de los 15 casos ejecutados es 15/15. Paneles: [`run1`](evidencias/testsprite/paneles/web-run1-6-15.png), [`run2`](evidencias/testsprite/paneles/web-run2-14-15.png) y [`run3`](evidencias/testsprite/paneles/web-run3-tc002-1-1.png).

### 7.3 Tabla de análisis de fallos de TestSprite

| Caso | Descripción | Resultado | Causa | Decisión |
| --- | --- | --- | --- | --- |
| API TC009 (run2) | El admin intenta cambiar su propio rol | Falló: esperaba 400 y recibió 200 | **Error del test generado:** envió `rol: "admin"` al admin, es decir, el mismo rol; la API solo rechaza un cambio real. | No se cambió el código. Se comprobó manualmente y con la prueba de integración que `rol: "usuario"` responde 400. Se repitió con esa instrucción (run3): pasó. |
| Web TC002 (run2) | Registro de una cuenta nueva | Falló: apareció “Ese email ya está registrado” | **Datos del test:** reutilizó un email registrado y borrado lógicamente en run1. Después de cambiar el email no volvió a pulsar «Crear cuenta». | No se cambió el código. Se repitió con un email nuevo y reenviando el formulario (run3): pasó. |
| Web run1 (9 casos) | Login, registro y CRUD | Bloqueados con página en blanco | **Entorno:** `vite dev` es mono-hilo y se saturó con las pruebas concurrentes de TestSprite. | Se generó el build de producción y se sirvió con `vite preview`; se agregó `preview.proxy` para `/api` en `web/vite.config.js`. En run2 no hubo bloqueos. |

Ningún fallo correspondió a un error real de la aplicación. El único cambio de código derivado de TestSprite fue la configuración del proxy del preview de producción.

### 7.4 Comparación con las pruebas escritas a mano

Las pruebas escritas a mano cubren con precisión las reglas que el equipo conoce: códigos HTTP, mensajes exactos, reglas de negocio, aislamiento con MongoDB en memoria y estados de la interfaz. TestSprite aportó una ejecución en navegador real y contra HTTP real sin mocks, generó un plan desde el PRD y descubrió una carencia real de configuración: el build de producción servido con `vite preview` no tenía proxy hacia la API. Ese hallazgo no lo cubrían Vitest ni Playwright porque ambos usan `vite dev`. En cambio, TestSprite no encontró errores funcionales nuevos y su plan se quedó en caminos felices: no generó casos de 401/403, ids mal formados, paginación fuera de rango, JSON inválido ni contraseñas débiles, que sí están en las 80 pruebas de API. Tampoco ejecutó los casos de perfil y contraseña de la web. Además produjo falsos positivos cuando el test reutilizó datos o interpretó mal una regla. Por eso TestSprite es útil como revisión independiente del contrato y del entorno real, pero no sustituye una suite automatizada mantenida con casos negativos y aserciones precisas.

## 8. Evidencias

| Evidencia | Archivo |
| --- | --- |
| `npm test` en la API (80 pruebas) | [`evidencias/coverage/api-tests.png`](evidencias/coverage/api-tests.png) |
| `npm test` en la web (129 pruebas) | [`evidencias/coverage/web-tests.png`](evidencias/coverage/web-tests.png) |
| Cobertura en terminal de la API | [`evidencias/coverage/api-coverage.png`](evidencias/coverage/api-coverage.png) |
| Cobertura en terminal de la web | [`evidencias/coverage/web-coverage.png`](evidencias/coverage/web-coverage.png) |
| Reporte HTML de cobertura de la API | [`evidencias/coverage/api-coverage-html.png`](evidencias/coverage/api-coverage-html.png) |
| `app.js` con líneas sin cubrir | [`evidencias/coverage/api-coverage-app-js.png`](evidencias/coverage/api-coverage-app-js.png) |
| Reporte HTML de cobertura de la web | [`evidencias/coverage/web-coverage-html.png`](evidencias/coverage/web-coverage-html.png) |
| `UsersView.vue` con detalle de cobertura | [`evidencias/coverage/web-coverage-usersview.png`](evidencias/coverage/web-coverage-usersview.png) |
| Resumen JSON de cobertura de la API | [`evidencias/coverage/api-coverage-summary.json`](evidencias/coverage/api-coverage-summary.json) |
| Resumen JSON de cobertura de la web | [`evidencias/coverage/web-coverage-summary.json`](evidencias/coverage/web-coverage-summary.json) |
| Reporte HTML de Playwright (29 pasan) | [`evidencias/playwright/playwright-report.png`](evidencias/playwright/playwright-report.png) |
| Plan y reporte de TestSprite de la API | [`evidencias/testsprite/api/testsprite-mcp-test-report.md`](evidencias/testsprite/api/testsprite-mcp-test-report.md) · [`HTML`](evidencias/testsprite/api/testsprite-mcp-test-report.html) |
| Plan y reporte de TestSprite de la web | [`evidencias/testsprite/web/testsprite-mcp-test-report.md`](evidencias/testsprite/web/testsprite-mcp-test-report.md) · [`HTML`](evidencias/testsprite/web/testsprite-mcp-test-report.html) |
| Panel de TestSprite — API (10/10) | [`evidencias/testsprite/paneles/api-final-run3-10-10.png`](evidencias/testsprite/paneles/api-final-run3-10-10.png) |
| Panel de TestSprite — web run2 (14/15) | [`evidencias/testsprite/paneles/web-run2-14-15.png`](evidencias/testsprite/paneles/web-run2-14-15.png) |
| Panel de TestSprite — web run3 TC002 (1/1) | [`evidencias/testsprite/paneles/web-run3-tc002-1-1.png`](evidencias/testsprite/paneles/web-run3-tc002-1-1.png) |
| Índice de evidencias TestSprite | [`evidencias/testsprite/README.md`](evidencias/testsprite/README.md) |

## 9. Lista de verificación

- [x] `npm install` y `npm test` funcionan en `api/` y `web/`.
- [x] `api/app.js` exporta la app sin llamar a `listen()`; `server.js` hace el arranque.
- [x] La API tiene 80 pruebas (mínimo 30) y la web 129 (mínimo 30), todas pasando.
- [x] `npm run coverage` cumple los umbrales en ambos proyectos.
- [x] `npm run test:e2e` pasa en Chromium y Firefox con la base `app-usuarios-e2e`.
- [x] Las pruebas no dependen del orden ni de datos de otra prueba.
- [x] Evidencias de TestSprite de API y web, con paneles, reportes y tabla de análisis de fallos.
- [x] No hay `.env`, API keys, `node_modules/`, `coverage/` ni `playwright-report/` en el repositorio.
- [x] `INFORME_PRUEBAS.md` incluye resumen, hallazgos y la sección de comparación con TestSprite.

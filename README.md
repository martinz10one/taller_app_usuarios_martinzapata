# App de usuarios — Taller de Pruebas de Software

Aplicación compuesta por una API REST (Node.js, Express, MongoDB y JWT) y una web (Vue 3, Vite y Vue Router), con pruebas unitarias, de integración, de componentes y end-to-end, reporte de cobertura y evidencias de ejecución.

## Contenido

- [Requisitos](#requisitos)
- [Puesta en marcha](#puesta-en-marcha)
- [Scripts](#scripts)
- [Pruebas y resultados](#pruebas-y-resultados)
- [Cobertura](#cobertura)
- [Pruebas end-to-end](#pruebas-end-to-end)
- [Pruebas con TestSprite](#pruebas-con-testsprite)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Evidencias](#evidencias)
- [Decisiones técnicas](#decisiones-técnicas)

## Requisitos

- Node.js 22 o superior (probado con Node 23.8.0).
- npm 10 o superior.
- MongoDB local para desarrollo y para las pruebas E2E. Las pruebas de la API usan MongoDB en memoria y no necesitan MongoDB instalado.

## Puesta en marcha

### API

```bash
cd api
cp .env.example .env       # ajustar MONGODB_CNX, JWT_SECRET y el admin inicial
npm install
npm run seed               # borra y carga los usuarios de prueba
npm run dev                # http://localhost:3000/api
```

Comprobar que responde:

```bash
curl http://localhost:3000/api/health
```

### Web

```bash
cd web
npm install
npm run dev                # http://localhost:5173
```

Cuentas de prueba del seed:

| Rol | Email | Contraseña |
| --- | --- | --- |
| Administrador | `admin@demo.com` | `Admin123!` |
| Administrador | `marta@demo.com` | `Usuario123` |
| Usuario | `ana@demo.com` | `Usuario123` |
| Usuario | `luis@demo.com` | `Usuario123` |
| Usuario desactivado | `pedro@demo.com` | `Usuario123` |

## Scripts

### `api/package.json`

| Script | Comando | Uso |
| --- | --- | --- |
| `dev` | `node --watch server.js` | Desarrollo con recarga |
| `start` | `node server.js` | Producción |
| `seed` | `node database/seed.js` | Reiniciar datos de ejemplo |
| `test` | `vitest run` | Pruebas unitarias y de integración |
| `test:watch` | `vitest` | Pruebas en modo vigilancia |
| `coverage` | `vitest run --coverage` | Pruebas + reporte de cobertura |

### `web/package.json`

| Script | Comando | Uso |
| --- | --- | --- |
| `dev` | `vite` | Desarrollo |
| `build` | `vite build` | Compilar para producción |
| `preview` | `vite preview` | Previsualizar la compilación |
| `test` | `vitest run` | Pruebas unitarias, de componentes y del router |
| `test:watch` | `vitest` | Pruebas en modo vigilancia |
| `coverage` | `vitest run --coverage` | Pruebas + reporte de cobertura |
| `test:e2e` | `playwright test` | Pruebas end-to-end en Chromium y Firefox |

## Pruebas y resultados

| Proyecto | Herramientas | Pruebas | Estado |
| --- | --- | --- | --- |
| API | Vitest + Supertest + `mongodb-memory-server` | 80 | 80 pasan, 0 fallan |
| Web (unitaria/componentes) | Vitest + Vue Test Utils + jsdom | 129 | 129 pasan, 0 fallan |
| Web (E2E) | Playwright + Chromium + Firefox | 29 | 29 pasan, 0 fallan |
| API (TestSprite MCP) | TestSprite + `PRD.md` | 10 | 10 pasan, 0 fallan |
| Web (TestSprite MCP) | TestSprite + `PRD.md` | 15 ejecutados de 28 planificados | 15 pasan, 0 fallan |

Comandos:

```bash
# API
cd api && npm test && npm run coverage

# Web: pruebas de Vitest y cobertura
cd web && npm test && npm run coverage

# Web: end-to-end (requiere MongoDB local)
cd web && npx playwright install chromium firefox && npm run test:e2e
```

Las pruebas de la API se ejecutan contra una instancia de MongoDB en memoria (`mongodb-memory-server`), se limpian antes de cada prueba y no tocan la base de datos de desarrollo. Las pruebas de la web limpian `localStorage` y restauran los mocks antes de cada caso. No se usan `.skip` ni `.only`.

## Cobertura

Umbrales configurados en ambos proyectos: **80 %** de líneas, funciones y sentencias, y **70 %** de ramas. `npm run coverage` falla si no se cumplen.

| Proyecto | Sentencias | Ramas | Funciones | Líneas |
| --- | --- | --- | --- | --- |
| API | 95,02 % | 89,10 % | 100 % | 95,02 % |
| Web | 100 % | 95,64 % | 93,81 % | 100 % |

Resúmenes en JSON: [`evidencias/coverage/api-coverage-summary.json`](evidencias/coverage/api-coverage-summary.json) y [`evidencias/coverage/web-coverage-summary.json`](evidencias/coverage/web-coverage-summary.json).

## Pruebas end-to-end

La configuración está en [`web/playwright.config.js`](web/playwright.config.js):

- `webServer` levanta la API en el puerto 3000 con la base `app-usuarios-e2e` y la web en el puerto 5173.
- El proyecto `setup` guarda la sesión del administrador en `web/e2e/.auth/admin.json`; los proyectos `chromium` y `firefox` reutilizan ese `storageState`.
- Los flujos que necesitan empezar sin sesión limpian el estado con `test.use({ storageState: { cookies: [], origins: [] } })`.
- Se ejecuta con un solo worker para que las pruebas que crean datos no se pisen entre sí.
- Las capturas y trazas de fallos se guardan en `web/test-results/` y el reporte HTML en `web/playwright-report/`; ambas carpetas están excluidas del repositorio.

Pruebas incluidas:

- Login incorrecto y registro de cuenta nueva.
- Redirecciones por sesión y por rol.
- CRUD del administrador con búsqueda, filtro por rol, paginación y borrado lógico.
- Cambio de contraseña y login con la nueva contraseña.
- Restauración de la sesión al recargar.
- Página 404.
- Accesibilidad con Axe en login y listado de usuarios (sin violaciones graves ni críticas).

## Pruebas con TestSprite

Se ejecutó el servidor MCP oficial de TestSprite con el documento de requisitos [`PRD.md`](PRD.md), tanto contra la API (puerto 3000) como contra la web (puerto 5173). Las ejecuciones, los casos generados, los paneles y el análisis de fallos están en [`evidencias/testsprite/`](evidencias/testsprite/README.md).

| Proyecto | Ejecuciones | Casos ejecutados | Resultado final |
| --- | --- | --- | --- |
| API | 3 | 10 | 10/10 (run3) |
| Web | 3 | 15 de 28 planificados | 15/15 (run2 14/15 + repetición dirigida de TC002) |

- Reporte API: [`evidencias/testsprite/api/testsprite-mcp-test-report.md`](evidencias/testsprite/api/testsprite-mcp-test-report.md) · [`HTML`](evidencias/testsprite/api/testsprite-mcp-test-report.html)
- Reporte web: [`evidencias/testsprite/web/testsprite-mcp-test-report.md`](evidencias/testsprite/web/testsprite-mcp-test-report.md) · [`HTML`](evidencias/testsprite/web/testsprite-mcp-test-report.html)
- Paneles de TestSprite: [`API 10/10`](evidencias/testsprite/paneles/api-final-run3-10-10.png), [`web run2 14/15`](evidencias/testsprite/paneles/web-run2-14-15.png), [`web run3 TC002 1/1`](evidencias/testsprite/paneles/web-run3-tc002-1-1.png).

Los dos fallos intermedios se analizaron y resultaron ser defectos de los tests generados, no de la aplicación:

- **API TC009 (run2):** el test envió `rol: "admin"` al propio admin (el mismo rol), así que el 200 era correcto. Con `rol: "usuario"` la API responde 400 `No puedes cambiar tu propio rol`, como confirman la prueba de integración y la repetición (run3).
- **Web TC002 (run2):** el test reutilizó un email ya registrado y borrado lógicamente, y tras cambiar el correo no volvió a enviar el formulario. Con un email nuevo y un segundo envío, la repetición (run3) pasó.

La ejecución web 1 con `vite dev` quedó bloqueada en 9 casos porque el servidor de desarrollo es mono-hilo. Se pasó a un build de producción con `vite preview` y se añadió `preview.proxy` para `/api`; ese fue el hallazgo real de TestSprite y está corregido en [`web/vite.config.js`](web/vite.config.js).

## Estructura del proyecto

```text
.
├── api/
│   ├── app.js                 # crea y exporta la app de Express (sin listen)
│   ├── server.js              # conecta la base, crea el admin inicial y llama a listen
│   ├── controllers/           # lógica de auth y usuarios
│   ├── database/              # conexión y seed
│   ├── helpers/               # JWT, validadores y reglas de usuario
│   ├── middlewares/           # validarCampos, validarJWT y validarRol
│   ├── models/usuario.js      # schema, hash, validarPassword y toJSON
│   ├── routes/                # rutas y validaciones con express-validator
│   ├── tests/
│   │   ├── setup.js           # MongoDB en memoria y limpieza
│   │   ├── helpers.js         # crearUsuario, tokenAdmin, tokenUsuario
│   │   ├── unit/              # middlewares, helpers y modelo
│   │   └── integration/       # auth, usuarios y rutas generales con Supertest
│   └── vitest.config.js
├── web/
│   ├── src/
│   │   ├── components/        # FormField, PaginationBar, ConfirmDialog, etc.
│   │   ├── composables/       # useAuth y useToast
│   │   ├── services/          # http y clientes de auth/usuarios
│   │   ├── utils/             # validadores del cliente
│   │   ├── views/             # login, registro, perfil, usuarios y 404
│   │   └── router/index.js    # guardas requiresAuth, guestOnly y requiresAdmin
│   ├── tests/                 # pruebas de Vitest
│   ├── e2e/                   # pruebas de Playwright
│   ├── vitest.config.js
│   └── playwright.config.js
├── evidencias/
│   ├── coverage/              # capturas, reportes HTML y resúmenes JSON
│   ├── playwright/            # captura del reporte HTML
│   └── testsprite/            # plan, casos y reportes de TestSprite
├── PRD.md                     # requisitos usados por TestSprite
├── INFORME_PRUEBAS.md         # informe final del taller
└── README.md
```

## Evidencias

| Evidencia | Archivo |
| --- | --- |
| `npm test` en la API | [`evidencias/coverage/api-tests.png`](evidencias/coverage/api-tests.png) |
| `npm test` en la web | [`evidencias/coverage/web-tests.png`](evidencias/coverage/web-tests.png) |
| Cobertura en terminal (API) | [`evidencias/coverage/api-coverage.png`](evidencias/coverage/api-coverage.png) |
| Cobertura en terminal (web) | [`evidencias/coverage/web-coverage.png`](evidencias/coverage/web-coverage.png) |
| Reporte HTML de cobertura (API) | [`evidencias/coverage/api-coverage-html.png`](evidencias/coverage/api-coverage-html.png) |
| Archivo con líneas sin cubrir (API) | [`evidencias/coverage/api-coverage-app-js.png`](evidencias/coverage/api-coverage-app-js.png) |
| Reporte HTML de cobertura (web) | [`evidencias/coverage/web-coverage-html.png`](evidencias/coverage/web-coverage-html.png) |
| Archivo con líneas sin cubrir (web) | [`evidencias/coverage/web-coverage-usersview.png`](evidencias/coverage/web-coverage-usersview.png) |
| Reporte HTML de Playwright | [`evidencias/playwright/playwright-report.png`](evidencias/playwright/playwright-report.png) |
| Reportes de TestSprite (API y web) | [`evidencias/testsprite/api/`](evidencias/testsprite/api/) · [`evidencias/testsprite/web/`](evidencias/testsprite/web/) |
| Paneles de TestSprite | [`evidencias/testsprite/paneles/`](evidencias/testsprite/paneles/) |

## Decisiones técnicas

- **Separación `app.js` / `server.js`**: permite que Supertest use la app sin abrir un puerto. `app.js` solo crea y exporta Express; `server.js` conecta MongoDB, crea el administrador inicial y escucha.
- **Vitest 3.2.7**: es la versión compatible con Node 23.8.0 y con `@vitest/coverage-v8` de la misma versión.
- **MongoDB en memoria**: las pruebas de integración no dependen de una instalación local ni dejan datos.
- **Base E2E independiente**: Playwright usa `app-usuarios-e2e` porque `npm run seed` borra la colección.
- **Accesibilidad**: se corrigió el contraste del texto atenuado y el subrayado de los enlaces en `web/src/assets/main.css` para cumplir WCAG AA, en lugar de relajar las aserciones de Axe.
- **Proxy también en `preview`**: además de `server.proxy`, `web/vite.config.js` define `preview.proxy` para `/api`. Lo detectó TestSprite: el build de producción servido con `vite preview` no podía autenticarse ni cargar datos.
- **TestSprite como revisión externa**: se usó para contrastar el contrato descrito en `PRD.md` contra la API y la web reales. Sus resultados se revisaron y clasificaron; no se aceptaron automáticamente ni se alteró la aplicación para “hacer pasar” un test generado.
- **Sin credenciales en el repositorio**: `.env`, la API key de TestSprite, `node_modules/`, `coverage/`, `playwright-report/`, `test-results/`, `testsprite_tests/` y `e2e/.auth/` están excluidos. Los JWT incrustados en los casos de TestSprite se redactaron en las copias de evidencia.

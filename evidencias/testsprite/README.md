# Evidencias de TestSprite (MCP)

Pruebas generadas y ejecutadas con el agente de IA de TestSprite sobre la App de usuarios, usando [`PRD.md`](../../PRD.md) como fuente de requisitos. Estas evidencias se obtuvieron con ejecuciones reales; no se inventaron resultados.

## Entorno usado

| Elemento | Valor |
|---|---|
| API | `http://localhost:3000` con MongoDB local `app-usuarios-testsprite` |
| Web | `http://localhost:5173` (primera ejecución con `vite dev`; segunda y tercera con `vite preview` del build de producción) |
| PRD | `PRD.md` de la raíz del repositorio |
| Autenticación API | header `x-token` con JWT de administrador (4 h) |
| Autenticación web | `admin@demo.com` / `Admin123!` |
| Servidor MCP | `@testsprite/testsprite-mcp@0.0.47` |

La API key de TestSprite **no está en el repositorio**. Los JWT que TestSprite incrustó en los casos generados fueron reemplazados por `<ADMIN_JWT_REDACTED>` en las copias de evidencia.

## API

| Ejecución | Fecha | Total | ✅ Passed | ❌ Failed | ⛔ Blocked | Evidencia |
|---|---|---:|---:|---:|---:|---|
| run1 | 2026-10-26 | 10 | 10 | 0 | 0 | [`api/ejecuciones/run1/`](api/ejecuciones/run1/) |
| run2 | 2026-10-26 | 10 | 9 | 1 | 0 | [`api/ejecuciones/run2/`](api/ejecuciones/run2/) |
| run3 | 2026-10-26 | 10 | 10 | 0 | 0 | [`api/ejecuciones/run3/`](api/ejecuciones/run3/) |

- Plan: [`api/plan/testsprite_backend_test_plan.json`](api/plan/testsprite_backend_test_plan.json)
- Reporte completo: [`api/testsprite-mcp-test-report.md`](api/testsprite-mcp-test-report.md) · [`HTML`](api/testsprite-mcp-test-report.html)
- Panel local: [`paneles/api-final-run3-10-10.png`](paneles/api-final-run3-10-10.png)
- Panel del fallo analizado: [`paneles/api-run2-9-10.png`](paneles/api-run2-9-10.png)

## Web

| Ejecución | Entorno | Seleccionados | ✅ Passed | ❌ Failed | ⛔ Blocked | Evidencia |
|---|---|---:|---:|---:|---:|---|
| run1 | `vite dev` | 15 | 6 | 0 | 9 | [`web/ejecuciones/run1/`](web/ejecuciones/run1/) |
| run2 | `vite preview` | 15 | 14 | 1 | 0 | [`web/ejecuciones/run2/`](web/ejecuciones/run2/) |
| run3 | `vite preview`, solo TC002 | 1 | 1 | 0 | 0 | [`web/ejecuciones/run3/`](web/ejecuciones/run3/) |

- Plan: [`web/plan/testsprite_frontend_test_plan.json`](web/plan/testsprite_frontend_test_plan.json)
- Reporte completo: [`web/testsprite-mcp-test-report.md`](web/testsprite-mcp-test-report.md) · [`HTML`](web/testsprite-mcp-test-report.html)
- Paneles locales: [`run1`](paneles/web-run1-6-15.png) · [`run2`](paneles/web-run2-14-15.png) · [`run3`](paneles/web-run3-tc002-1-1.png)

## Análisis de fallos y decisiones

| Caso | Descripción | Resultado | Causa | Decisión |
|---|---|---|---|---|
| API TC009 (run2) | El admin “cambia” su propio rol | Falló: esperaba 400 y recibió 200 | **Error del test generado:** envió `rol: "admin"` al admin, es decir, el mismo rol. La API solo rechaza un cambio real. | No se tocó el código. Se verificó manualmente y con Vitest que `rol: "usuario"` sí responde 400. Se repitió con esa instrucción (run3): pasó. |
| Web TC002 (run2) | Registro de una cuenta nueva | Falló: el formulario mostró “Ese email ya está registrado” | **Datos del test:** reutilizó un email registrado y borrado lógicamente en run1. Además, tras cambiar el email no volvió a pulsar «Crear cuenta». | No se tocó el código. Se repitió con un email nuevo y reenviando el formulario (run3): pasó. |
| Web run1 (9 casos) | Login, registro y CRUD | Bloqueados con página en blanco | **Entorno:** `vite dev` es mono-hilo y se saturó con las pruebas concurrentes de TestSprite. | Se generó el build de producción y se sirvió con `vite preview`. Se agregó `preview.proxy` para `/api` en `web/vite.config.js`. En run2 ya no hubo bloqueos. |

## Hallazgos

1. **Configuración de despliegue:** el `vite preview` no tenía proxy hacia la API; sin él, el build de producción no podía iniciar sesión ni cargar datos. Se corrigió en `web/vite.config.js`.
2. **Regla de auto-protección del admin:** la API responde 400 `No puedes cambiar tu propio rol` cuando el cambio es real. El fallo de TestSprite fue un falso positivo.
3. **Email de cuentas borradas:** el índice único mantiene reservado el email de un usuario con borrado lógico; es el comportamiento esperado y obliga a usar emails nuevos en pruebas repetidas.
4. **Cobertura del plan:** TestSprite priorizó caminos felices. Los casos negativos (401/403, validaciones, paginación, JSON inválido) siguen cubiertos por Vitest/Supertest, no por TestSprite.

## Comparación con las pruebas escritas a mano

TestSprite aportó una ejecución en navegador real y contra HTTP real sin mocks, y descubrió un problema de configuración del preview de producción. No encontró errores funcionales nuevos en la aplicación. Las pruebas manuales (80 de API, 129 de web y 29 ejecuciones E2E en Chromium/Firefox) cubren muchos más casos negativos, aislamiento con MongoDB en memoria y regresiones concretas. El detalle de la comparación está en [`INFORME_PRUEBAS.md`](../../INFORME_PRUEBAS.md).

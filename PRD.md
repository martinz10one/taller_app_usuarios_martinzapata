# PRD — App de usuarios (API REST + web)

Documento de requisitos usado como entrada para las pruebas asistidas por IA con TestSprite.

## 1. Objetivo

Permitir que una persona se registre, inicie sesión y administre su perfil, y que un administrador gestione el ciclo de vida de los usuarios (crear, consultar, editar y eliminar lógicamente) desde una aplicación web protegida por roles.

## 2. Alcance y arquitectura

| Componente | Tecnología | URL local |
| --- | --- | --- |
| API | Node.js + Express + MongoDB (Mongoose) + JWT | `http://localhost:3000/api` |
| Web | Vue 3 + Vite + Vue Router | `http://localhost:5173` |
| Autenticación | JWT enviado en el header `x-token` | — |
| Base de datos de pruebas E2E | MongoDB local, base `app-usuarios-e2e` | — |

La API expone JSON. Todas las respuestas de error usan `{ "error": "mensaje" }` o, en errores de validación, `{ "errores": [{ "path": "campo", "msg": "mensaje" }] }`.

## 3. Roles y autorización

| Rol | Permisos |
| --- | --- |
| `usuario` | Registrarse, iniciar sesión, ver y editar su propio perfil, cambiar su contraseña. |
| `admin` | Todo lo anterior y el CRUD completo de usuarios. |

Reglas de autorización:

- El registro público siempre crea rol `usuario`, aunque el cuerpo incluya `rol: "admin"`.
- Las rutas de `/api/usuarios` exigen token válido y rol `admin`.
- Token ausente → `401`; token inválido o expirado → `401`; rol insuficiente → `403`.
- Un usuario desactivado no puede iniciar sesión ni usar un token emitido antes de su desactivación.

## 4. Reglas de contraseña

La contraseña debe:

- Tener entre 8 y 64 caracteres.
- Incluir al menos una letra mayúscula.
- Incluir al menos una letra minúscula.
- Incluir al menos un número.

El nombre debe tener entre 2 y 60 caracteres. El email debe tener formato válido y ser único (sin distinguir mayúsculas ni espacios).

## 5. Endpoints de autenticación

| Método y ruta | Acceso | Comportamiento esperado |
| --- | --- | --- |
| `POST /api/auth/registro` | Público | Crea un usuario con rol `usuario`. Responde `201` con `{ token, usuario }`, sin `password` en la respuesta. Email duplicado → `400`. Datos inválidos → `400`. |
| `POST /api/auth/login` | Público | Credenciales correctas → `200` con `{ token, usuario }` (el usuario incluye `uid`). Contraseña incorrecta o email inexistente → `401` con el mismo mensaje `Credenciales inválidas`. Usuario desactivado → `401` con `Usuario desactivado`. |
| `GET /api/auth/perfil` | Token | Devuelve el perfil del usuario autenticado. Sin token o token inválido → `401`. |
| `PUT /api/auth/perfil` | Token | Actualiza `nombre` y/o `email` del usuario autenticado. Email de otro usuario → `400`. |
| `PUT /api/auth/password` | Token | Exige `passwordActual` y `passwordNueva`. Contraseña actual incorrecta → `400`. Nueva igual a la actual → `400`. Éxito → `200` con `{ "mensaje": "Contraseña actualizada" }`; el login posterior debe funcionar con la nueva. |

## 6. Endpoints de administración de usuarios

Todos requieren token de administrador.

| Método y ruta | Comportamiento esperado |
| --- | --- |
| `GET /api/usuarios` | Lista solo usuarios activos. Parámetros opcionales: `buscar` (nombre o email, búsqueda literal e insensible a mayúsculas), `rol` (`admin` o `usuario`), `pagina` (entero ≥ 1, por defecto 1) y `limite` (entero 1–50, por defecto 10). Responde `{ total, pagina, limite, totalPaginas, usuarios }`. Los usuarios se ordenan alfabéticamente por nombre. |
| `GET /api/usuarios/:id` | Devuelve el usuario activo. Id mal formado → `400`; inexistente o desactivado → `404`. |
| `POST /api/usuarios` | Crea un usuario con nombre, email, contraseña y rol opcional. `201` con el usuario creado. La contraseña se guarda hasheada. |
| `PUT /api/usuarios/:id` | Actualización parcial. `password` vacía o ausente no cambia la contraseña. Id inválido → `400`; usuario inexistente o desactivado → `404`. |
| `DELETE /api/usuarios/:id` | Borrado lógico: marca `estado: false`. Responde `200` con `{ mensaje: "Usuario eliminado", usuario }`. El usuario desaparece del listado y ya no puede iniciar sesión. Id inválido → `400`; inexistente o ya desactivado → `404`. |

## 7. Reglas de negocio del administrador

- Un administrador no puede cambiar su propio rol: `PUT /api/usuarios/:id` con su propio `id` y un rol distinto → `400` con `No puedes cambiar tu propio rol`.
- Un administrador no puede eliminarse a sí mismo: `DELETE /api/usuarios/:id` con su propio `id` → `400` con `No puedes eliminar tu propia cuenta`.
- Un administrador sí puede cambiar el rol de otro usuario y editar sus datos.
- Siempre debe quedar al menos un administrador activo como consecuencia de las dos reglas anteriores.

## 8. Requisitos de la aplicación web

| Ruta | Acceso | Comportamiento |
| --- | --- | --- |
| `/login` | Solo invitados | Formulario de email y contraseña. Error del servidor visible. Si ya hay sesión, redirige al inicio según el rol. |
| `/registro` | Solo invitados | Crea una cuenta y deja la sesión iniciada. |
| `/perfil` | Autenticado | Muestra nombre, email y rol; permite editar nombre/email y cambiar contraseña. |
| `/usuarios` | Solo admin | Listado con búsqueda, filtro por rol, paginación y acciones de editar/eliminar. Un usuario normal es redirigido a `/perfil`. |
| `/usuarios/nuevo` | Solo admin | Formulario de creación. |
| `/usuarios/:id/editar` | Solo admin | Formulario de edición; un admin no puede cambiarse el rol a sí mismo. |
| Ruta desconocida | Público | Página 404 con enlace para volver al inicio. |

Comportamiento de la interfaz:

- La sesión se guarda en `localStorage` (`x-token`) y se restaura al recargar la página.
- Sin sesión, una ruta protegida redirige a `/login` conservando el destino en `?redirect=`.
- La búsqueda del listado espera un breve debounce antes de consultar.
- El listado muestra 8 usuarios por página.
- Eliminar un usuario exige confirmación en un diálogo.
- Los avisos de éxito o error se muestran como notificaciones temporales (toasts).
- Los formularios muestran mensajes por campo y un mensaje general cuando la API falla.

## 9. Requisitos no funcionales

- `GET /api/health` responde `200` con `{ "status": "ok" }`.
- Una ruta inexistente responde `404` en JSON con `Ruta no encontrada`.
- Un cuerpo con JSON mal formado responde `400` con `El cuerpo de la petición no es un JSON válido`.
- Las contraseñas nunca se devuelven en las respuestas ni se almacenan en texto plano.
- La API debe poder probarse sin abrir un puerto (Supertest) y sin tocar la base de datos real (MongoDB en memoria).
- La aplicación debe funcionar en Chromium y Firefox.
- La interfaz debe cumplir WCAG 2.0/2.1 nivel A y AA en las pantallas de login y listado de usuarios, sin violaciones graves o críticas detectadas por Axe.

## 10. Cuentas de prueba del seed

| Rol | Email | Contraseña |
| --- | --- | --- |
| Administrador | `admin@demo.com` | `Admin123!` |
| Administrador | `marta@demo.com` | `Usuario123` |
| Usuario | `ana@demo.com` | `Usuario123` |
| Usuario | `luis@demo.com` | `Usuario123` |
| Usuario desactivado | `pedro@demo.com` | `Usuario123` |

El comando `npm run seed` en `api/` borra la colección y vuelve a cargar estas cuentas. Por eso las pruebas E2E usan la base `app-usuarios-e2e`, nunca la base de desarrollo.

## 11. Criterios de aceptación para TestSprite

1. Todos los endpoints y reglas de los apartados 3 a 7 deben tener al menos un caso positivo y uno negativo.
2. Los flujos web del apartado 8 deben poder completarse con las cuentas del seed.
3. Cualquier diferencia entre el resultado observado y este PRD debe registrarse en el informe con su causa y decisión (error real, requisito mal interpretado o problema del entorno).

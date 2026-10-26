import { expect } from "@playwright/test";

export const PASSWORD = "Usuario123";
export const ADMIN = { email: "admin@demo.com", password: "Admin123!" };
export const USUARIO = { email: "ana@demo.com", password: PASSWORD };

/** Inicia sesión desde la pantalla de login y espera a salir de ella. */
export async function iniciarSesion(page, { email, password }) {
  await page.goto("/login");
  await page.getByTestId("login-email").fill(email);
  await page.getByTestId("login-password").fill(password);
  await page.getByTestId("login-submit").click();
  await expect(page).not.toHaveURL(/\/login/);
}

/** Token de administrador para preparar datos directamente por la API. */
export async function tokenAdminPorApi(request) {
  const login = await request.post("http://localhost:3000/api/auth/login", {
    data: ADMIN,
  });
  expect(login.ok()).toBeTruthy();
  const { token } = await login.json();
  return token;
}

/** Crea un usuario por la API y devuelve los datos enviados. */
export async function crearUsuarioPorApi(request, datos) {
  const token = await tokenAdminPorApi(request);
  const respuesta = await request.post("http://localhost:3000/api/usuarios", {
    headers: { "x-token": token },
    data: { password: PASSWORD, rol: "usuario", ...datos },
  });
  expect(respuesta.ok()).toBeTruthy();
  return { password: PASSWORD, rol: "usuario", ...datos };
}

/** Crea usuarios por la API para preparar datos de paginación sin repetir la UI. */
export async function crearUsuariosPorApi(request, cantidad, prefijo = "e2e") {
  const token = await tokenAdminPorApi(request);

  for (let i = 1; i <= cantidad; i += 1) {
    const respuesta = await request.post("http://localhost:3000/api/usuarios", {
      headers: { "x-token": token },
      data: {
        nombre: `${prefijo} ${i}`,
        email: `${prefijo}${i}@demo.com`,
        password: PASSWORD,
        rol: "usuario",
      },
    });
    expect(respuesta.ok()).toBeTruthy();
  }
}

export const emailUnico = (prefijo) => `${prefijo}-${Date.now()}@demo.com`;

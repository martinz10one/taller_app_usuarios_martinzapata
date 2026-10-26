import { test, expect } from "@playwright/test";
import { PASSWORD, USUARIO, emailUnico, iniciarSesion } from "./helpers.js";

// Estos flujos necesitan empezar sin la sesión guardada del administrador.
test.use({ storageState: { cookies: [], origins: [] } });

test("login con credenciales incorrectas muestra el alert y sigue en /login", async ({ page }) => {
  await page.goto("/login");
  await page.getByTestId("login-email").fill("ana@demo.com");
  await page.getByTestId("login-password").fill("Incorrecta123");
  await page.getByTestId("login-submit").click();

  await expect(page.getByTestId("alert")).toContainText("Credenciales inválidas");
  await expect(page).toHaveURL(/\/login/);
});

test("registro de una cuenta nueva entra al perfil con rol Usuario", async ({ page }) => {
  const email = emailUnico("registro");

  await page.goto("/registro");
  await page.getByTestId("register-name").fill("Persona Registrada");
  await page.getByTestId("register-email").fill(email);
  await page.getByTestId("register-password").fill(PASSWORD);
  await page.getByTestId("register-confirmation").fill(PASSWORD);
  await page.getByTestId("register-submit").click();

  await expect(page).toHaveURL(/\/perfil/);
  await expect(page.getByTestId("profile-role")).toHaveText("Usuario");
  await expect(page.getByTestId("current-user-name")).toContainText("Persona Registrada");
});

test("un usuario normal que abre /usuarios es enviado a /perfil", async ({ page }) => {
  await iniciarSesion(page, USUARIO);

  await page.goto("/usuarios");

  await expect(page).toHaveURL(/\/perfil/);
  await expect(page.getByTestId("profile-role")).toHaveText("Usuario");
});

test("sin sesión, /usuarios redirige a /login", async ({ page }) => {
  await page.goto("/usuarios");

  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByTestId("login-form")).toBeVisible();
});

test("el usuario cambia su contraseña, cierra sesión y entra con la nueva", async ({ page }) => {
  const email = emailUnico("password");
  const nuevaPassword = "NuevaPassword123";

  await page.goto("/registro");
  await page.getByTestId("register-name").fill("Usuario Password");
  await page.getByTestId("register-email").fill(email);
  await page.getByTestId("register-password").fill(PASSWORD);
  await page.getByTestId("register-confirmation").fill(PASSWORD);
  await page.getByTestId("register-submit").click();
  await expect(page).toHaveURL(/\/perfil/);

  await page.getByTestId("password-current").fill(PASSWORD);
  await page.getByTestId("password-new").fill(nuevaPassword);
  await page.getByTestId("password-confirmation").fill(nuevaPassword);
  await page.getByTestId("password-submit").click();
  await expect(page.getByTestId("toast").filter({ hasText: "Contraseña actualizada" })).toBeVisible();

  await page.getByTestId("logout").click();
  await expect(page).toHaveURL(/\/login/);

  await page.getByTestId("login-email").fill(email);
  await page.getByTestId("login-password").fill(nuevaPassword);
  await page.getByTestId("login-submit").click();

  await expect(page).toHaveURL(/\/perfil/);
  await expect(page.getByTestId("current-user-name")).toContainText("Usuario Password");
});

test("una ruta que no existe muestra la página no encontrada", async ({ page }) => {
  await page.goto("/esta-ruta-no-existe");

  await expect(page.getByText("Página no encontrada")).toBeVisible();
  await expect(page.getByText("404")).toBeVisible();
  await expect(page.getByTestId("go-home")).toBeVisible();
});

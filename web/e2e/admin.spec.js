import { test, expect } from "@playwright/test";
import { PASSWORD, crearUsuarioPorApi, crearUsuariosPorApi, emailUnico } from "./helpers.js";

test("el admin ve la lista de usuarios al entrar", async ({ page }) => {
  await page.goto("/usuarios");

  await expect(page).toHaveURL(/\/usuarios/);
  await expect(page.getByTestId("user-row").first()).toBeVisible();
  await expect(page.getByTestId("users-total")).toContainText("usuarios activos");
});

test("el admin crea un usuario, lo busca y lo edita", async ({ page }) => {
  const email = emailUnico("creado");
  const nombre = `Usuario Creado ${Date.now()}`;
  const nombreEditado = `${nombre} Editado`;

  await page.goto("/usuarios");
  await page.getByTestId("users-new").click();
  await expect(page).toHaveURL(/\/usuarios\/nuevo/);

  await page.getByTestId("user-name").fill(nombre);
  await page.getByTestId("user-email").fill(email);
  await page.getByTestId("user-password").fill(PASSWORD);
  await page.getByTestId("user-submit").click();

  await expect(page).toHaveURL(/\/usuarios$/);
  await page.getByTestId("users-search").fill(email);
  const fila = page.getByTestId("user-row").filter({ hasText: email });
  await expect(fila).toBeVisible();

  await fila.getByTestId("user-edit").click();
  await expect(page).toHaveURL(/\/editar$/);
  await page.getByTestId("user-name").fill(nombreEditado);
  await page.getByTestId("user-submit").click();

  await expect(page).toHaveURL(/\/usuarios$/);
  await page.getByTestId("users-search").fill(nombreEditado);
  await expect(page.getByTestId("user-row").filter({ hasText: email })).toBeVisible();
});

test("el admin elimina un usuario y ese usuario ya no puede iniciar sesión", async ({ page, request }) => {
  const email = emailUnico("borrado");
  const usuario = await crearUsuarioPorApi(request, {
    nombre: "Usuario Para Borrar",
    email,
  });

  await page.goto("/usuarios");
  await page.getByTestId("users-search").fill(email);
  const fila = page.getByTestId("user-row").filter({ hasText: email });
  await expect(fila).toBeVisible();

  await fila.getByTestId("user-delete").click();
  await expect(page.getByTestId("confirm-dialog")).toBeVisible();
  await page.getByTestId("confirm-accept").click();

  await expect(page.getByTestId("toast")).toContainText("eliminado");
  await expect(page.getByTestId("users-empty")).toContainText("Ningún usuario coincide");

  await page.getByTestId("logout").click();
  await expect(page).toHaveURL(/\/login/);

  await page.getByTestId("login-email").fill(usuario.email);
  await page.getByTestId("login-password").fill(usuario.password);
  await page.getByTestId("login-submit").click();

  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByTestId("alert")).toContainText("Usuario desactivado");
});

test("el filtro por rol y la paginación cambian el listado", async ({ page, request }) => {
  const prefijo = `pag-${Date.now()}`;
  await crearUsuariosPorApi(request, 10, prefijo);

  await page.goto("/usuarios");
  await page.getByTestId("users-role-filter").selectOption("usuario");

  await expect(page.getByTestId("pagination-info")).toContainText("Mostrando 1–8");
  await expect(page.getByTestId("pagination-prev")).toBeDisabled();

  await page.getByTestId("pagination-next").click();

  await expect(page.getByTestId("pagination-page")).toContainText("Página 2 de");
  await expect(page.getByTestId("pagination-info")).not.toContainText("Mostrando 1–8");
  await expect(page.getByTestId("pagination-prev")).toBeEnabled();
  await expect(page.getByTestId("user-row").first()).toBeVisible();
});

test("el admin puede filtrar por administradores", async ({ page }) => {
  await page.goto("/usuarios");

  await page.getByTestId("users-role-filter").selectOption("admin");

  await expect(page.getByTestId("user-row").first()).toBeVisible();
  await expect(page.getByTestId("users-total")).toContainText("2 usuarios activos");
});

test("la sesión del admin se restaura al recargar la página", async ({ page }) => {
  await page.goto("/usuarios");

  // Esperar a que la vista haya cargado los datos antes de recargar:
  // así la prueba comprueba la restauración de sesión y no una carrera de hidratación.
  await expect(page.getByTestId("user-row").first()).toBeVisible();
  await expect(page.getByTestId("current-user-name")).toHaveText("Administrador");

  await page.reload();

  await expect(page).toHaveURL(/\/usuarios/);
  await expect(page.getByTestId("current-user-name")).toHaveText("Administrador");
  await expect(page.getByTestId("user-row").first()).toBeVisible();
});

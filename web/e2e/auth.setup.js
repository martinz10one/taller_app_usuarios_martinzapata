import { mkdir } from "node:fs/promises";
import { test as setup, expect } from "@playwright/test";
import { ADMIN } from "./helpers.js";

const archivoAdmin = "e2e/.auth/admin.json";

setup("guarda la sesión del administrador", async ({ page }) => {
  await mkdir("e2e/.auth", { recursive: true });

  await page.goto("/login");
  await page.getByTestId("login-email").fill(ADMIN.email);
  await page.getByTestId("login-password").fill(ADMIN.password);
  await page.getByTestId("login-submit").click();

  await expect(page).toHaveURL(/\/usuarios/);
  await expect(page.getByTestId("user-row").first()).toBeVisible();

  await page.context().storageState({ path: archivoAdmin });
});

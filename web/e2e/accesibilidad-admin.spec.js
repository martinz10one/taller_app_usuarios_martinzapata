import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("el listado de usuarios no tiene violaciones graves de accesibilidad", async ({ page }) => {
  await page.goto("/usuarios");

  // Analizar con la tabla ya poblada: si se escanea antes, Axe revisa
  // el estado vacío y no el contenido real del listado.
  await expect(page.getByTestId("user-row").first()).toBeVisible();
  await expect(page.getByTestId("users-total")).toContainText("usuarios activos");

  const resultados = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
  const graves = resultados.violations.filter((violacion) =>
    ["serious", "critical"].includes(violacion.impact),
  );

  expect(graves).toEqual([]);
});

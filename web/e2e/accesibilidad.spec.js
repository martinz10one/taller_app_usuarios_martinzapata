import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.use({ storageState: { cookies: [], origins: [] } });

test("la pantalla de login no tiene violaciones graves de accesibilidad", async ({ page }) => {
  await page.goto("/login");

  const resultados = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
  const graves = resultados.violations.filter((violacion) =>
    ["serious", "critical"].includes(violacion.impact),
  );

  expect(graves).toEqual([]);
});

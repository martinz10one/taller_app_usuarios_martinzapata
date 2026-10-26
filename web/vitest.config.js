import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config.js";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "jsdom",
      // Solo las pruebas de Vitest; e2e/ pertenece a Playwright y tiene su propio runner.
      include: ["tests/**/*.test.js"],
      setupFiles: ["./tests/setup.js"],
      clearMocks: true,
      restoreMocks: true,
      coverage: {
        provider: "v8",
        reporter: ["text", "html", "json-summary"],
        include: ["src/**/*.{js,vue}"],
        exclude: ["src/main.js"],
        thresholds: {
          lines: 80,
          functions: 80,
          statements: 80,
          branches: 70,
        },
      },
    },
  }),
);

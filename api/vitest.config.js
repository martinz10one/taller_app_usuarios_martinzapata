import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    setupFiles: ["./tests/setup.js"],
    // Todas las suites comparten una única base en memoria:
    // se ejecutan en serie para que la limpieza de una no afecte a otra.
    fileParallelism: false,
    env: {
      NODE_ENV: "test",
      JWT_SECRET: "secreto-de-pruebas-suficientemente-largo",
      JWT_EXPIRA: "4h",
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "json-summary"],
      include: [
        "app.js",
        "controllers/**",
        "middlewares/**",
        "helpers/**",
        "models/**",
        "routes/**",
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        statements: 80,
        branches: 70,
      },
    },
  },
});

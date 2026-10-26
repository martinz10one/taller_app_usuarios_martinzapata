import { describe, expect, it } from "vitest";
import { emailExiste, esRolValido } from "../../helpers/db-validators.js";
import { crearUsuario } from "../helpers.js";

describe("esRolValido", () => {
  it("acepta los roles admin y usuario", () => {
    expect(esRolValido("admin")).toBe(true);
    expect(esRolValido("usuario")).toBe(true);
  });

  it("rechaza un rol desconocido con un mensaje útil", () => {
    expect(() => esRolValido("superadmin")).toThrow("El rol debe ser uno de: admin, usuario");
  });
});

describe("emailExiste", () => {
  it("permite un email que no está registrado", async () => {
    await expect(emailExiste("nuevo@test.com")).resolves.toBeUndefined();
  });

  it("rechaza un email ya registrado por otro usuario", async () => {
    const usuario = await crearUsuario({ email: "ocupado@test.com" });
    await expect(emailExiste("ocupado@test.com")).rejects.toThrow("Ese email ya está registrado");
    expect(usuario.email).toBe("ocupado@test.com");
  });

  it("no considera duplicado el email del propio usuario que se edita", async () => {
    const usuario = await crearUsuario({ email: "propio@test.com" });
    await expect(emailExiste(usuario.email, usuario.id)).resolves.toBeUndefined();
  });

  it("normaliza mayúsculas y espacios antes de buscar", async () => {
    await crearUsuario({ email: "normalizado@test.com" });
    await expect(emailExiste("  NORMALIZADO@test.com  ")).rejects.toThrow("Ese email ya está registrado");
  });
});

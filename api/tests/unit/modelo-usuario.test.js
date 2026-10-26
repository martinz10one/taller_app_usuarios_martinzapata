import { describe, expect, it } from "vitest";
import Usuario from "../../models/usuario.js";
import { crearUsuario } from "../helpers.js";

describe("modelo Usuario", () => {
  it("hashea la contraseña antes de guardar", async () => {
    const usuario = await crearUsuario({ email: "hash@test.com", password: "Password123" });
    const guardado = await Usuario.findById(usuario.id).select("+password");

    expect(guardado.password).not.toBe("Password123");
    expect(guardado.password.startsWith("$2")).toBe(true);
  });

  it("validarPassword acepta la contraseña correcta y rechaza la incorrecta", async () => {
    const usuario = await crearUsuario({ password: "Password123" });

    expect(usuario.validarPassword("Password123")).toBe(true);
    expect(usuario.validarPassword("OtraPassword123")).toBe(false);
  });

  it("toJSON no devuelve password ni _id y agrega uid", async () => {
    const usuario = await crearUsuario({ email: "json@test.com" });
    const json = usuario.toJSON();

    expect(json).not.toHaveProperty("password");
    expect(json).not.toHaveProperty("_id");
    expect(json).not.toHaveProperty("__v");
    expect(json.uid.toString()).toBe(usuario.id);
    expect(json.email).toBe("json@test.com");
  });

  it("aplica valores por defecto de rol y estado", async () => {
    const usuario = new Usuario({ nombre: "Sin rol", email: "default@test.com", password: "Password123" });
    await usuario.save();

    expect(usuario.rol).toBe("usuario");
    expect(usuario.estado).toBe(true);
  });

  it("rechaza un rol que no está en el enum", async () => {
    const usuario = new Usuario({
      nombre: "Rol inválido",
      email: "rol@test.com",
      password: "Password123",
      rol: "superadmin",
    });

    await expect(usuario.save()).rejects.toThrow();
  });
});

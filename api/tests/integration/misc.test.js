import request from "supertest";
import { afterEach, describe, expect, it, vi } from "vitest";
import app from "../../app.js";
import Usuario from "../../models/usuario.js";
import { tokenAdmin } from "../helpers.js";

afterEach(() => {
  vi.restoreAllMocks();
});

const datosNuevoUsuario = {
  nombre: "Usuario Con Error",
  email: "error@test.com",
  password: "Password123",
};

describe("rutas generales de la API", () => {
  it("GET /api/health responde 200 con { status: 'ok' }", async () => {
    const res = await request(app).get("/api/health");

    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: "ok" });
  });

  it("una ruta inexistente responde 404 en JSON", async () => {
    const res = await request(app).get("/api/no-existe");

    expect(res.status).toBe(404);
    expect(res.headers["content-type"]).toMatch(/json/);
    expect(res.body).toEqual({ error: "Ruta no encontrada" });
  });

  it("un body con JSON mal formado responde 400 con un mensaje claro", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app)
      .post("/api/usuarios")
      .set("x-token", token)
      .set("Content-Type", "application/json")
      .send('{"nombre": "roto"');

    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "El cuerpo de la petición no es un JSON válido" });
  });
});

describe("manejo de errores de persistencia", () => {
  it("responde 400 si el índice único de MongoDB detecta un email duplicado al guardar", async () => {
    const { token } = await tokenAdmin();
    vi.spyOn(Usuario.prototype, "save").mockRejectedValueOnce(
      Object.assign(new Error("E11000 duplicate key"), { code: 11000 }),
    );

    const res = await request(app).post("/api/usuarios").set("x-token", token).send(datosNuevoUsuario);

    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "Ese email ya está registrado" });
  });

  it("responde 400 con el mensaje del Schema ante un ValidationError", async () => {
    const { token } = await tokenAdmin();
    vi.spyOn(Usuario.prototype, "save").mockRejectedValueOnce(
      Object.assign(new Error("Usuario validation failed"), { name: "ValidationError" }),
    );

    const res = await request(app).post("/api/usuarios").set("x-token", token).send(datosNuevoUsuario);

    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "Usuario validation failed" });
  });

  it("responde 500 con un mensaje genérico ante un error inesperado", async () => {
    const { token } = await tokenAdmin();
    const log = vi.spyOn(console, "log").mockImplementation(() => {});
    vi.spyOn(Usuario.prototype, "save").mockRejectedValueOnce(new Error("fallo inesperado"));

    const res = await request(app).post("/api/usuarios").set("x-token", token).send(datosNuevoUsuario);

    expect(res.status).toBe(500);
    expect(res.body).toEqual({ error: "Error interno" });
    expect(log).toHaveBeenCalledWith("ERROR:", "fallo inesperado");
  });
});

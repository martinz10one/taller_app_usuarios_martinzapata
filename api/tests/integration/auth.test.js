import request from "supertest";
import { describe, expect, it } from "vitest";
import app from "../../app.js";
import { crearUsuario, tokenAdmin } from "../helpers.js";

describe("POST /api/auth/registro", () => {
  it("con datos válidos responde 201, devuelve token y rol usuario aunque se envíe admin", async () => {
    const res = await request(app).post("/api/auth/registro").send({
      nombre: "Nueva Persona",
      email: "nueva@test.com",
      password: "Password123",
      rol: "admin",
    });

    expect(res.status).toBe(201);
    expect(res.body.token).toEqual(expect.any(String));
    expect(res.body.usuario.rol).toBe("usuario");
    expect(res.body.usuario.email).toBe("nueva@test.com");
    expect(res.body.usuario.uid).toEqual(expect.any(String));
    expect(res.body.usuario).not.toHaveProperty("password");
  });

  it("con un email ya registrado responde 400 y el error apunta al campo email", async () => {
    await crearUsuario({ email: "repetido@test.com" });

    const res = await request(app).post("/api/auth/registro").send({
      nombre: "Otra Persona",
      email: "repetido@test.com",
      password: "Password123",
    });

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({ path: "email", msg: "Ese email ya está registrado" });
  });

  it("rechaza una contraseña sin mayúscula", async () => {
    const res = await request(app).post("/api/auth/registro").send({
      nombre: "Sin Mayúscula",
      email: "sinmayuscula@test.com",
      password: "password123",
    });

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({
      path: "password",
      msg: "La contraseña debe incluir al menos una mayúscula",
    });
  });

  it("rechaza una contraseña de menos de 8 caracteres", async () => {
    const res = await request(app).post("/api/auth/registro").send({
      nombre: "Corta",
      email: "corta@test.com",
      password: "Ab1",
    });

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({
      path: "password",
      msg: "La contraseña debe tener entre 8 y 64 caracteres",
    });
  });

  it("rechaza nombre vacío y email con formato inválido", async () => {
    const res = await request(app).post("/api/auth/registro").send({
      nombre: "",
      email: "correo-invalido",
      password: "Password123",
    });

    expect(res.status).toBe(400);
    expect(res.body.errores.map((error) => error.path)).toEqual(expect.arrayContaining(["nombre", "email"]));
  });
});

describe("POST /api/auth/login", () => {
  it("con credenciales correctas responde 200 con token y usuario con uid", async () => {
    const usuario = await crearUsuario({ email: "login@test.com", password: "Password123" });

    const res = await request(app)
      .post("/api/auth/login")
      .send({ email: "LOGIN@test.com", password: "Password123" });

    expect(res.status).toBe(200);
    expect(res.body.token).toEqual(expect.any(String));
    expect(res.body.usuario.uid).toBe(usuario.id);
    expect(res.body.usuario).not.toHaveProperty("password");
  });

  it("con contraseña incorrecta responde 401 con el mensaje genérico", async () => {
    await crearUsuario({ email: "mala@test.com", password: "Password123" });

    const res = await request(app)
      .post("/api/auth/login")
      .send({ email: "mala@test.com", password: "Incorrecta123" });

    expect(res.status).toBe(401);
    expect(res.body).toEqual({ error: "Credenciales inválidas" });
  });

  it("con un email inexistente responde el mismo mensaje que una contraseña incorrecta", async () => {
    const res = await request(app)
      .post("/api/auth/login")
      .send({ email: "nadie@test.com", password: "Password123" });

    expect(res.status).toBe(401);
    expect(res.body).toEqual({ error: "Credenciales inválidas" });
  });

  it("un usuario desactivado no puede iniciar sesión", async () => {
    await crearUsuario({ email: "inactivo@test.com", password: "Password123", estado: false });

    const res = await request(app)
      .post("/api/auth/login")
      .send({ email: "inactivo@test.com", password: "Password123" });

    expect(res.status).toBe(401);
    expect(res.body).toEqual({ error: "Usuario desactivado" });
  });

  it("rechaza un email mal formado o una contraseña vacía", async () => {
    const res = await request(app).post("/api/auth/login").send({ email: "mal", password: "" });

    expect(res.status).toBe(400);
    expect(res.body.errores.map((error) => error.path)).toEqual(expect.arrayContaining(["email", "password"]));
  });
});

describe("GET /api/auth/perfil", () => {
  it("sin token responde 401", async () => {
    const res = await request(app).get("/api/auth/perfil");
    expect(res.status).toBe(401);
  });

  it("con un token inválido responde 401", async () => {
    const res = await request(app).get("/api/auth/perfil").set("x-token", "no-es-un-jwt");
    expect(res.status).toBe(401);
    expect(res.body).toEqual({ error: "Token no válido o expirado" });
  });

  it("con un token válido responde 200 con el perfil", async () => {
    const { token, usuario } = await tokenAdmin();

    const res = await request(app).get("/api/auth/perfil").set("x-token", token);

    expect(res.status).toBe(200);
    expect(res.body.uid).toBe(usuario.id);
    expect(res.body.email).toBe(usuario.email);
    expect(res.body).not.toHaveProperty("password");
  });
});

describe("PUT /api/auth/perfil", () => {
  it("actualiza nombre y email del usuario autenticado", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app)
      .put("/api/auth/perfil")
      .set("x-token", token)
      .send({ nombre: "Nombre Nuevo", email: "perfil-nuevo@test.com" });

    expect(res.status).toBe(200);
    expect(res.body.nombre).toBe("Nombre Nuevo");
    expect(res.body.email).toBe("perfil-nuevo@test.com");
  });

  it("no permite usar el email de otro usuario", async () => {
    await crearUsuario({ email: "ocupado@test.com" });
    const { token } = await tokenAdmin();

    const res = await request(app)
      .put("/api/auth/perfil")
      .set("x-token", token)
      .send({ email: "ocupado@test.com" });

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({ path: "email", msg: "Ese email ya está registrado" });
  });

  it("rechaza un nombre demasiado corto", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).put("/api/auth/perfil").set("x-token", token).send({ nombre: "A" });

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({
      path: "nombre",
      msg: "El nombre debe tener entre 2 y 60 caracteres",
    });
  });
});

describe("PUT /api/auth/password", () => {
  it("rechaza una contraseña actual incorrecta", async () => {
    const { token } = await tokenAdmin({ password: "Password123" });

    const res = await request(app)
      .put("/api/auth/password")
      .set("x-token", token)
      .send({ passwordActual: "NoEsLaActual123", passwordNueva: "NuevaPassword123" });

    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "La contraseña actual no es correcta" });
  });

  it("rechaza que la nueva contraseña sea igual a la actual", async () => {
    const { token } = await tokenAdmin({ password: "Password123" });

    const res = await request(app)
      .put("/api/auth/password")
      .set("x-token", token)
      .send({ passwordActual: "Password123", passwordNueva: "Password123" });

    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "La nueva contraseña debe ser distinta de la actual" });
  });

  it("rechaza una nueva contraseña que no cumple las reglas", async () => {
    const { token } = await tokenAdmin({ password: "Password123" });

    const res = await request(app)
      .put("/api/auth/password")
      .set("x-token", token)
      .send({ passwordActual: "Password123", passwordNueva: "corta" });

    expect(res.status).toBe(400);
    expect(res.body.errores.map((error) => error.path)).toContain("passwordNueva");
  });

  it("exige la contraseña actual", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app)
      .put("/api/auth/password")
      .set("x-token", token)
      .send({ passwordNueva: "NuevaPassword123" });

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({
      path: "passwordActual",
      msg: "La contraseña actual es obligatoria",
    });
  });

  it("cambia la contraseña y luego el login funciona con la nueva", async () => {
    const { token } = await tokenAdmin({ email: "cambio@test.com", password: "Password123" });

    const cambio = await request(app)
      .put("/api/auth/password")
      .set("x-token", token)
      .send({ passwordActual: "Password123", passwordNueva: "NuevaPassword123" });

    expect(cambio.status).toBe(200);
    expect(cambio.body).toEqual({ mensaje: "Contraseña actualizada" });

    const conNueva = await request(app)
      .post("/api/auth/login")
      .send({ email: "cambio@test.com", password: "NuevaPassword123" });
    expect(conNueva.status).toBe(200);

    const conVieja = await request(app)
      .post("/api/auth/login")
      .send({ email: "cambio@test.com", password: "Password123" });
    expect(conVieja.status).toBe(401);
  });
});

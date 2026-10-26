import mongoose from "mongoose";
import request from "supertest";
import { describe, expect, it } from "vitest";
import app from "../../app.js";
import Usuario from "../../models/usuario.js";
import { crearUsuario, tokenAdmin, tokenUsuario } from "../helpers.js";

describe("GET /api/usuarios — autenticación y autorización", () => {
  it("sin token responde 401", async () => {
    const res = await request(app).get("/api/usuarios");
    expect(res.status).toBe(401);
    expect(res.body).toEqual({ error: "No hay token en la petición" });
  });

  it("con token de rol usuario responde 403", async () => {
    const { token } = await tokenUsuario();

    const res = await request(app).get("/api/usuarios").set("x-token", token);

    expect(res.status).toBe(403);
    expect(res.body).toEqual({ error: "No tiene permisos para esto" });
  });
});

describe("GET /api/usuarios — listado y paginación", () => {
  it("el admin recibe total, pagina, limite, totalPaginas y usuarios activos", async () => {
    const { token } = await tokenAdmin();
    await crearUsuario({ nombre: "Activo Uno" });
    await crearUsuario({ nombre: "Activo Dos" });
    await crearUsuario({ nombre: "Eliminado", estado: false });

    const res = await request(app).get("/api/usuarios").set("x-token", token);

    expect(res.status).toBe(200);
    expect(res.body).toMatchObject({ total: 3, pagina: 1, limite: 10, totalPaginas: 1 });
    expect(res.body.usuarios).toHaveLength(3);
    expect(res.body.usuarios.every((usuario) => usuario.estado)).toBe(true);
    expect(res.body.usuarios[0]).not.toHaveProperty("password");
  });

  it("ordena por nombre y respeta pagina y limite", async () => {
    const { token } = await tokenAdmin({ nombre: "Admin Orden" });
    for (const nombre of ["Carlos", "Ana", "Beatriz", "Daniel", "Elena"]) {
      await crearUsuario({ nombre });
    }

    const primera = await request(app)
      .get("/api/usuarios?pagina=1&limite=2")
      .set("x-token", token);
    const segunda = await request(app)
      .get("/api/usuarios?pagina=2&limite=2")
      .set("x-token", token);

    expect(primera.status).toBe(200);
    expect(primera.body.total).toBe(6);
    expect(primera.body.totalPaginas).toBe(3);
    expect(primera.body.usuarios[0].nombre).toBe("Admin Orden");
    expect(segunda.status).toBe(200);
    expect(segunda.body.pagina).toBe(2);
    expect(segunda.body.usuarios).toHaveLength(2);
  });

  it("responde 400 si el límite es mayor que 50", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).get("/api/usuarios?limite=51").set("x-token", token);

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({ path: "limite", msg: "El límite debe estar entre 1 y 50" });
  });

  it("responde 400 si la página es cero o negativa", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).get("/api/usuarios?pagina=0").set("x-token", token);

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({
      path: "pagina",
      msg: "La página debe ser un entero mayor que 0",
    });
  });

  it("responde 400 si el rol del filtro no es válido", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).get("/api/usuarios?rol=superadmin").set("x-token", token);

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({
      path: "rol",
      msg: "El rol debe ser uno de: admin, usuario",
    });
  });

  it("busca por nombre o email y combina con el filtro de rol", async () => {
    const { token } = await tokenAdmin();
    await crearUsuario({ nombre: "Ana Torres", email: "ana.torres@test.com", rol: "usuario" });
    await crearUsuario({ nombre: "Ana Admin", email: "ana.admin@test.com", rol: "admin" });
    await crearUsuario({ nombre: "Luis Gómez", email: "luis@test.com", rol: "usuario" });

    const porNombre = await request(app)
      .get("/api/usuarios?buscar=ana&rol=usuario")
      .set("x-token", token);
    expect(porNombre.status).toBe(200);
    expect(porNombre.body.usuarios).toHaveLength(1);
    expect(porNombre.body.usuarios[0].email).toBe("ana.torres@test.com");

    const porEmail = await request(app)
      .get("/api/usuarios?buscar=luis@test")
      .set("x-token", token);
    expect(porEmail.status).toBe(200);
    expect(porEmail.body.usuarios).toHaveLength(1);
    expect(porEmail.body.usuarios[0].nombre).toBe("Luis Gómez");
  });

  it("trata los caracteres especiales de la búsqueda como texto literal", async () => {
    const { token } = await tokenAdmin();
    await crearUsuario({ nombre: "Usuario (especial)", email: "especial@test.com" });

    const res = await request(app)
      .get("/api/usuarios?buscar=(especial)")
      .set("x-token", token);

    expect(res.status).toBe(200);
    expect(res.body.usuarios).toHaveLength(1);
  });

  it("con un solo usuario devuelve total 1 y totalPaginas 1", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).get("/api/usuarios").set("x-token", token);

    expect(res.status).toBe(200);
    expect(res.body).toMatchObject({ total: 1, totalPaginas: 1 });
    expect(res.body.usuarios).toHaveLength(1);
  });
});

describe("GET /api/usuarios/:id", () => {
  it("responde 400 si el id no tiene formato de Mongo", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).get("/api/usuarios/abc").set("x-token", token);

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({ path: "id", msg: "Id no válido" });
  });

  it("responde 404 si el id es válido pero no existe", async () => {
    const { token } = await tokenAdmin();
    const id = new mongoose.Types.ObjectId().toString();

    const res = await request(app).get(`/api/usuarios/${id}`).set("x-token", token);

    expect(res.status).toBe(404);
    expect(res.body).toEqual({ error: "Usuario no encontrado" });
  });

  it("responde 404 si el usuario está desactivado", async () => {
    const { token } = await tokenAdmin();
    const eliminado = await crearUsuario({ estado: false });

    const res = await request(app).get(`/api/usuarios/${eliminado.id}`).set("x-token", token);

    expect(res.status).toBe(404);
  });

  it("devuelve el usuario cuando existe y está activo", async () => {
    const { token } = await tokenAdmin();
    const usuario = await crearUsuario({ email: "consulta@test.com" });

    const res = await request(app).get(`/api/usuarios/${usuario.id}`).set("x-token", token);

    expect(res.status).toBe(200);
    expect(res.body.uid).toBe(usuario.id);
    expect(res.body).not.toHaveProperty("_id");
  });
});

describe("POST /api/usuarios", () => {
  it("el admin crea un usuario y la contraseña queda hasheada en la base", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).post("/api/usuarios").set("x-token", token).send({
      nombre: "Creado Por Admin",
      email: "creado@test.com",
      password: "Password123",
      rol: "admin",
    });

    expect(res.status).toBe(201);
    expect(res.body.email).toBe("creado@test.com");
    expect(res.body.rol).toBe("admin");
    expect(res.body).not.toHaveProperty("password");

    const guardado = await Usuario.findOne({ email: "creado@test.com" }).select("+password");
    expect(guardado.password).not.toBe("Password123");
    expect(guardado.password.startsWith("$2")).toBe(true);
  });

  it("rechaza un rol inexistente", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).post("/api/usuarios").set("x-token", token).send({
      nombre: "Rol Malo",
      email: "rolmalo@test.com",
      password: "Password123",
      rol: "superadmin",
    });

    expect(res.status).toBe(400);
    expect(res.body.errores.map((error) => error.path)).toContain("rol");
  });

  it("rechaza un email ya registrado", async () => {
    const { token } = await tokenAdmin();
    await crearUsuario({ email: "duplicado@test.com" });

    const res = await request(app).post("/api/usuarios").set("x-token", token).send({
      nombre: "Duplicado",
      email: "duplicado@test.com",
      password: "Password123",
    });

    expect(res.status).toBe(400);
    expect(res.body.errores).toContainEqual({ path: "email", msg: "Ese email ya está registrado" });
  });

  it("rechaza una contraseña débil", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).post("/api/usuarios").set("x-token", token).send({
      nombre: "Débil",
      email: "debil@test.com",
      password: "sinmayuscula1",
    });

    expect(res.status).toBe(400);
    expect(res.body.errores.map((error) => error.path)).toContain("password");
  });
});

describe("PUT /api/usuarios/:id", () => {
  it("el admin no puede cambiar su propio rol", async () => {
    const { token, usuario } = await tokenAdmin();

    const res = await request(app)
      .put(`/api/usuarios/${usuario.id}`)
      .set("x-token", token)
      .send({ rol: "usuario" });

    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "No puedes cambiar tu propio rol" });
  });

  it("el admin sí puede cambiar el rol de otro usuario", async () => {
    const { token } = await tokenAdmin();
    const objetivo = await crearUsuario();

    const res = await request(app)
      .put(`/api/usuarios/${objetivo.id}`)
      .set("x-token", token)
      .send({ rol: "admin" });

    expect(res.status).toBe(200);
    expect(res.body.rol).toBe("admin");
  });

  it("con la contraseña vacía no la cambia y el login sigue funcionando", async () => {
    const { token } = await tokenAdmin();
    const objetivo = await crearUsuario({ email: "sincambio@test.com", password: "Password123" });

    const res = await request(app)
      .put(`/api/usuarios/${objetivo.id}`)
      .set("x-token", token)
      .send({ nombre: "Nombre Actualizado", password: "" });

    expect(res.status).toBe(200);
    expect(res.body.nombre).toBe("Nombre Actualizado");

    const login = await request(app)
      .post("/api/auth/login")
      .send({ email: "sincambio@test.com", password: "Password123" });
    expect(login.status).toBe(200);
  });

  it("cambia la contraseña de otro usuario cuando se envía una nueva válida", async () => {
    const { token } = await tokenAdmin();
    const objetivo = await crearUsuario({ email: "otro-cambio@test.com", password: "Password123" });

    const res = await request(app)
      .put(`/api/usuarios/${objetivo.id}`)
      .set("x-token", token)
      .send({ password: "NuevaPassword123" });

    expect(res.status).toBe(200);

    const login = await request(app)
      .post("/api/auth/login")
      .send({ email: "otro-cambio@test.com", password: "NuevaPassword123" });
    expect(login.status).toBe(200);
  });

  it("responde 404 si el usuario no existe o fue eliminado", async () => {
    const { token } = await tokenAdmin();
    const eliminado = await crearUsuario({ estado: false });

    const res = await request(app)
      .put(`/api/usuarios/${eliminado.id}`)
      .set("x-token", token)
      .send({ nombre: "No Debe Cambiar" });

    expect(res.status).toBe(404);
  });

  it("responde 400 si el id es inválido", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).put("/api/usuarios/abc").set("x-token", token).send({ nombre: "X Y" });

    expect(res.status).toBe(400);
  });
});

describe("DELETE /api/usuarios/:id — borrado lógico", () => {
  it("el admin no puede eliminarse a sí mismo", async () => {
    const { token, usuario } = await tokenAdmin();

    const res = await request(app).delete(`/api/usuarios/${usuario.id}`).set("x-token", token);

    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "No puedes eliminar tu propia cuenta" });
  });

  it("desactiva al usuario, lo saca del listado y le impide iniciar sesión", async () => {
    const { token } = await tokenAdmin();
    const objetivo = await crearUsuario({ email: "borrar@test.com", password: "Password123" });

    const res = await request(app).delete(`/api/usuarios/${objetivo.id}`).set("x-token", token);

    expect(res.status).toBe(200);
    expect(res.body.mensaje).toBe("Usuario eliminado");
    expect(res.body.usuario.estado).toBe(false);

    const listado = await request(app).get("/api/usuarios?limite=50").set("x-token", token);
    expect(listado.body.usuarios.map((usuario) => usuario.uid)).not.toContain(objetivo.id);

    const login = await request(app)
      .post("/api/auth/login")
      .send({ email: "borrar@test.com", password: "Password123" });
    expect(login.status).toBe(401);
    expect(login.body).toEqual({ error: "Usuario desactivado" });
  });

  it("responde 404 al intentar eliminar un usuario ya eliminado", async () => {
    const { token } = await tokenAdmin();
    const objetivo = await crearUsuario({ estado: false });

    const res = await request(app).delete(`/api/usuarios/${objetivo.id}`).set("x-token", token);

    expect(res.status).toBe(404);
  });

  it("responde 400 si el id no es válido", async () => {
    const { token } = await tokenAdmin();

    const res = await request(app).delete("/api/usuarios/123").set("x-token", token);

    expect(res.status).toBe(400);
  });
});

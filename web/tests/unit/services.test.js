import { beforeEach, describe, expect, it, vi } from "vitest";
import { authApi } from "@/services/authApi.js";
import { usersApi } from "@/services/usersApi.js";

const respuestaOk = (data = {}) => ({ ok: true, status: 200, json: vi.fn().mockResolvedValue(data) });

describe("clientes de la API", () => {
  let fetchMock;

  beforeEach(() => {
    fetchMock = vi.fn().mockResolvedValue(respuestaOk({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);
  });

  const ultimaLlamada = () => {
    const [url, opciones] = fetchMock.mock.calls.at(-1);
    return { url: String(url), opciones };
  };

  it("authApi.login hace POST /auth/login con el cuerpo", async () => {
    const datos = { email: "ana@demo.com", password: "Usuario123" };

    await authApi.login(datos);

    const { url, opciones } = ultimaLlamada();
    expect(url).toBe("http://localhost:3000/api/auth/login");
    expect(opciones.method).toBe("POST");
    expect(opciones.body).toBe(JSON.stringify(datos));
  });

  it("authApi.registro hace POST /auth/registro con el cuerpo", async () => {
    const datos = { nombre: "Ana", email: "ana@demo.com", password: "Usuario123" };

    await authApi.registro(datos);

    const { url, opciones } = ultimaLlamada();
    expect(url).toBe("http://localhost:3000/api/auth/registro");
    expect(opciones.method).toBe("POST");
    expect(opciones.body).toBe(JSON.stringify(datos));
  });

  it("authApi.perfil hace GET /auth/perfil", async () => {
    await authApi.perfil();

    const { url, opciones } = ultimaLlamada();
    expect(url).toBe("http://localhost:3000/api/auth/perfil");
    expect(opciones.method).toBe("GET");
    expect(opciones.body).toBeUndefined();
  });

  it("authApi.actualizarPerfil hace PUT /auth/perfil", async () => {
    const datos = { nombre: "Ana Nueva", email: "ana.nueva@demo.com" };

    await authApi.actualizarPerfil(datos);

    const { url, opciones } = ultimaLlamada();
    expect(url).toBe("http://localhost:3000/api/auth/perfil");
    expect(opciones.method).toBe("PUT");
    expect(opciones.body).toBe(JSON.stringify(datos));
  });

  it("authApi.cambiarPassword hace PUT /auth/password", async () => {
    const datos = { passwordActual: "Usuario123", passwordNueva: "NuevaPassword123" };

    await authApi.cambiarPassword(datos);

    const { url, opciones } = ultimaLlamada();
    expect(url).toBe("http://localhost:3000/api/auth/password");
    expect(opciones.method).toBe("PUT");
    expect(opciones.body).toBe(JSON.stringify(datos));
  });

  it("usersApi.listar envía solo los filtros con valor", async () => {
    await usersApi.listar({ buscar: "ana", rol: "", pagina: 2, limite: 8 });

    const { url, opciones } = ultimaLlamada();
    const parametros = new URL(url).searchParams;
    expect(url).toContain("http://localhost:3000/api/usuarios");
    expect(opciones.method).toBe("GET");
    expect(parametros.get("buscar")).toBe("ana");
    expect(parametros.get("pagina")).toBe("2");
    expect(parametros.get("limite")).toBe("8");
    expect(parametros.has("rol")).toBe(false);
  });

  it("usersApi.obtener codifica el id en la ruta", async () => {
    await usersApi.obtener("id con espacio");

    const { url, opciones } = ultimaLlamada();
    expect(url).toBe("http://localhost:3000/api/usuarios/id%20con%20espacio");
    expect(opciones.method).toBe("GET");
  });

  it("usersApi.crear hace POST /usuarios con el cuerpo", async () => {
    const datos = { nombre: "Nuevo", email: "nuevo@demo.com", password: "Usuario123", rol: "usuario" };

    await usersApi.crear(datos);

    const { url, opciones } = ultimaLlamada();
    expect(url).toBe("http://localhost:3000/api/usuarios");
    expect(opciones.method).toBe("POST");
    expect(opciones.body).toBe(JSON.stringify(datos));
  });

  it("usersApi.actualizar hace PUT /usuarios/:id", async () => {
    const datos = { nombre: "Editado" };

    await usersApi.actualizar("64b000000000000000000001", datos);

    const { url, opciones } = ultimaLlamada();
    expect(url).toBe("http://localhost:3000/api/usuarios/64b000000000000000000001");
    expect(opciones.method).toBe("PUT");
    expect(opciones.body).toBe(JSON.stringify(datos));
  });

  it("usersApi.eliminar hace DELETE /usuarios/:id", async () => {
    await usersApi.eliminar("64b000000000000000000002");

    const { url, opciones } = ultimaLlamada();
    expect(url).toBe("http://localhost:3000/api/usuarios/64b000000000000000000002");
    expect(opciones.method).toBe("DELETE");
    expect(opciones.body).toBeUndefined();
  });
});

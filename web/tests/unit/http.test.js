import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, request, setUnauthorizedHandler, tokenStorage } from "@/services/http.js";

const respuesta = (status, data) => ({
  ok: status >= 200 && status < 300,
  status,
  json: vi.fn().mockResolvedValue(data),
});

describe("request", () => {
  beforeEach(() => {
    setUnauthorizedHandler(() => {});
  });

  it("hace una petición GET sin token y sin Content-Type", async () => {
    const fetchMock = vi.fn().mockResolvedValue(respuesta(200, { ok: true }));
    vi.stubGlobal("fetch", fetchMock);

    const data = await request("/auth/perfil");

    expect(data).toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, options] = fetchMock.mock.calls[0];
    expect(String(url)).toBe("http://localhost:3000/api/auth/perfil");
    expect(options.method).toBe("GET");
    expect(options.headers).toEqual({ Accept: "application/json" });
    expect(options.body).toBeUndefined();
  });

  it("envía el header x-token cuando hay un token guardado", async () => {
    tokenStorage.set("token-secreto");
    const fetchMock = vi.fn().mockResolvedValue(respuesta(200, {}));
    vi.stubGlobal("fetch", fetchMock);

    await request("/auth/perfil");

    expect(fetchMock.mock.calls[0][1].headers["x-token"]).toBe("token-secreto");
  });

  it("serializa el body como JSON y usa el método indicado", async () => {
    const fetchMock = vi.fn().mockResolvedValue(respuesta(201, { uid: "1" }));
    vi.stubGlobal("fetch", fetchMock);

    await request("/usuarios", { method: "POST", body: { nombre: "Ana" } });

    const [, options] = fetchMock.mock.calls[0];
    expect(options.method).toBe("POST");
    expect(options.headers["Content-Type"]).toBe("application/json");
    expect(options.body).toBe(JSON.stringify({ nombre: "Ana" }));
  });

  it("agrega solo los parámetros de query con valor", async () => {
    const fetchMock = vi.fn().mockResolvedValue(respuesta(200, {}));
    vi.stubGlobal("fetch", fetchMock);

    await request("/usuarios", { query: { buscar: "ana", pagina: 2, rol: "", vacio: undefined } });

    const url = new URL(fetchMock.mock.calls[0][0]);
    expect(url.searchParams.get("buscar")).toBe("ana");
    expect(url.searchParams.get("pagina")).toBe("2");
    expect(url.searchParams.has("rol")).toBe(false);
    expect(url.searchParams.has("vacio")).toBe(false);
  });

  it("convierte { errores } en ApiError con details por campo", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        respuesta(400, {
          errores: [
            { path: "email", msg: "Ese email ya está registrado" },
            { path: "password", msg: "La contraseña es obligatoria" },
          ],
        }),
      ),
    );

    const error = await request("/auth/registro", { method: "POST", body: {} }).catch((e) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(400);
    expect(error.message).toBe("Revisa los datos del formulario");
    expect(error.details).toEqual({
      email: "Ese email ya está registrado",
      password: "La contraseña es obligatoria",
    });
  });

  it("convierte { error } en ApiError con ese mensaje", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respuesta(401, { error: "Credenciales inválidas" })));

    const error = await request("/auth/login", { method: "POST", body: {} }).catch((e) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(401);
    expect(error.message).toBe("Credenciales inválidas");
    expect(error.details).toEqual({});
  });

  it("si el cuerpo del error no es JSON usa un mensaje genérico", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 500, json: vi.fn().mockRejectedValue(new Error("sin json")) }),
    );

    const error = await request("/health").catch((e) => e);

    expect(error.message).toBe("Error 500");
  });

  it("si fetch falla lanza ApiError con status 0", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    const error = await request("/health").catch((e) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(0);
    expect(error.message).toContain("No se pudo conectar con el servidor");
  });

  it("con 401 y token guardado llama al manejador de sesión expirada", async () => {
    tokenStorage.set("token-vencido");
    const onUnauthorized = vi.fn();
    setUnauthorizedHandler(onUnauthorized);
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respuesta(401, { error: "Token no válido o expirado" })));

    await request("/auth/perfil").catch(() => {});

    expect(onUnauthorized).toHaveBeenCalledOnce();
  });

  it("con 401 sin token no llama al manejador de sesión expirada", async () => {
    const onUnauthorized = vi.fn();
    setUnauthorizedHandler(onUnauthorized);
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respuesta(401, { error: "Credenciales inválidas" })));

    await request("/auth/login", { method: "POST", body: {} }).catch(() => {});

    expect(onUnauthorized).not.toHaveBeenCalled();
  });
});

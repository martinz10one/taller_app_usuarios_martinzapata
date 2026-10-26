import { beforeEach, describe, expect, it, vi } from "vitest";

const authApiMocks = vi.hoisted(() => ({
  login: vi.fn(),
  registro: vi.fn(),
  perfil: vi.fn(),
  actualizarPerfil: vi.fn(),
  cambiarPassword: vi.fn(),
}));

vi.mock("@/services/authApi.js", () => ({ authApi: authApiMocks }));

const USUARIO = { uid: "2", nombre: "Ana", email: "ana@demo.com", rol: "usuario" };
const ADMIN = { uid: "1", nombre: "Marta", email: "marta@demo.com", rol: "admin" };

const cargarRouter = async (usuario = null, path = "/") => {
  vi.resetModules();
  localStorage.clear();
  window.history.replaceState(null, "", "/");

  const { useAuth } = await import("@/composables/useAuth.js");
  if (usuario) {
    authApiMocks.login.mockResolvedValue({ token: "token-de-prueba", usuario });
    await useAuth().login({});
  }

  const router = (await import("@/router/index.js")).default;
  await router.push(path);
  await router.isReady();
  return { router, useAuth };
};

describe("guardas del router", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("sin sesión, /perfil redirige a login con redirect", async () => {
    const { router } = await cargarRouter(null, "/perfil");

    expect(router.currentRoute.value.name).toBe("login");
    expect(router.currentRoute.value.query.redirect).toBe("/perfil");
  });

  it("sin sesión, /usuarios redirige a login", async () => {
    const { router } = await cargarRouter(null, "/usuarios");

    expect(router.currentRoute.value.name).toBe("login");
  });

  it("un usuario normal que abre /usuarios es enviado a /perfil", async () => {
    const { router } = await cargarRouter(USUARIO, "/usuarios");

    expect(router.currentRoute.value.name).toBe("profile");
  });

  it("un admin puede entrar a /usuarios", async () => {
    const { router } = await cargarRouter(ADMIN, "/usuarios");

    expect(router.currentRoute.value.name).toBe("users");
  });

  it("un usuario autenticado que abre /login es enviado a su inicio", async () => {
    const { router } = await cargarRouter(USUARIO, "/login");

    expect(router.currentRoute.value.name).toBe("profile");
  });

  it("un admin autenticado que abre /login es enviado a usuarios", async () => {
    const { router } = await cargarRouter(ADMIN, "/login");

    expect(router.currentRoute.value.name).toBe("users");
  });

  it("la raíz redirige según el rol", async () => {
    const usuario = await cargarRouter(USUARIO, "/");
    expect(usuario.router.currentRoute.value.name).toBe("profile");

    const admin = await cargarRouter(ADMIN, "/");
    expect(admin.router.currentRoute.value.name).toBe("users");
  });

  it("una ruta inexistente muestra not-found", async () => {
    const { router } = await cargarRouter(null, "/no-existe");

    expect(router.currentRoute.value.name).toBe("not-found");
  });

  it("afterEach actualiza el título del documento", async () => {
    const { router } = await cargarRouter(null, "/login");

    expect(document.title).toBe("Iniciar sesión · Gestión de usuarios");
    expect(router.currentRoute.value.name).toBe("login");
  });
});

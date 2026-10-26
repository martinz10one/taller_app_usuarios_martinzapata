import { beforeEach, describe, expect, it, vi } from "vitest";

const authApiMocks = vi.hoisted(() => ({
  login: vi.fn(),
  registro: vi.fn(),
  perfil: vi.fn(),
  actualizarPerfil: vi.fn(),
  cambiarPassword: vi.fn(),
}));

vi.mock("@/services/authApi.js", () => ({ authApi: authApiMocks }));

const cargarUseAuth = async () => {
  vi.resetModules();
  const { useAuth } = await import("@/composables/useAuth.js");
  return useAuth();
};

const USUARIO = { uid: "64b000000000000000000001", nombre: "Ana", email: "ana@demo.com", rol: "usuario" };

describe("useAuth", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("login guarda el token y el usuario", async () => {
    authApiMocks.login.mockResolvedValue({ token: "token-login", usuario: USUARIO });
    const auth = await cargarUseAuth();

    await auth.login({ email: "ana@demo.com", password: "Usuario123" });

    expect(authApiMocks.login).toHaveBeenCalledWith({ email: "ana@demo.com", password: "Usuario123" });
    expect(auth.state.user).toEqual(USUARIO);
    expect(auth.state.token).toBe("token-login");
    expect(localStorage.getItem("x-token")).toBe("token-login");
    expect(auth.isAuthenticated.value).toBe(true);
  });

  it("register guarda la sesión creada", async () => {
    authApiMocks.registro.mockResolvedValue({ token: "token-registro", usuario: { ...USUARIO, rol: "usuario" } });
    const auth = await cargarUseAuth();

    await auth.register({ nombre: "Ana", email: "ana@demo.com", password: "Usuario123" });

    expect(auth.state.token).toBe("token-registro");
    expect(localStorage.getItem("x-token")).toBe("token-registro");
  });

  it("logout limpia el token, el usuario y localStorage", async () => {
    authApiMocks.login.mockResolvedValue({ token: "token-login", usuario: USUARIO });
    const auth = await cargarUseAuth();
    await auth.login({});

    auth.logout();

    expect(auth.state.user).toBeNull();
    expect(auth.state.token).toBeNull();
    expect(localStorage.getItem("x-token")).toBeNull();
    expect(auth.isAuthenticated.value).toBe(false);
  });

  it("isAdmin es true solo con rol admin", async () => {
    const auth = await cargarUseAuth();

    auth.setUser({ ...USUARIO, rol: "admin" });
    expect(auth.isAdmin.value).toBe(true);

    auth.setUser(USUARIO);
    expect(auth.isAdmin.value).toBe(false);
  });

  it("restoreSession sin token termina sin llamar a la API", async () => {
    const auth = await cargarUseAuth();

    await auth.restoreSession();

    expect(authApiMocks.perfil).not.toHaveBeenCalled();
    expect(auth.state.loaded).toBe(true);
    expect(auth.isAuthenticated.value).toBe(false);
  });

  it("restoreSession con token recupera el perfil de la API", async () => {
    localStorage.setItem("x-token", "token-guardado");
    authApiMocks.perfil.mockResolvedValue(USUARIO);
    const auth = await cargarUseAuth();

    await auth.restoreSession();

    expect(authApiMocks.perfil).toHaveBeenCalledOnce();
    expect(auth.state.user).toEqual(USUARIO);
    expect(auth.state.loaded).toBe(true);
    expect(auth.isAuthenticated.value).toBe(true);
  });

  it("restoreSession con un token inválido limpia la sesión", async () => {
    localStorage.setItem("x-token", "token-vencido");
    authApiMocks.perfil.mockRejectedValue(new Error("Token no válido"));
    const auth = await cargarUseAuth();

    await auth.restoreSession();

    expect(auth.state.user).toBeNull();
    expect(auth.state.token).toBeNull();
    expect(localStorage.getItem("x-token")).toBeNull();
  });

  it("restoreSession no vuelve a consultar si la sesión ya se cargó", async () => {
    localStorage.setItem("x-token", "token-guardado");
    authApiMocks.perfil.mockResolvedValue(USUARIO);
    const auth = await cargarUseAuth();
    await auth.restoreSession();

    await auth.restoreSession();

    expect(authApiMocks.perfil).toHaveBeenCalledOnce();
  });
});

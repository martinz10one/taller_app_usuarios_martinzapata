import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

const authApiMocks = vi.hoisted(() => ({
  login: vi.fn(),
  registro: vi.fn(),
  perfil: vi.fn(),
  actualizarPerfil: vi.fn(),
  cambiarPassword: vi.fn(),
}));

vi.mock("@/services/authApi.js", () => ({ authApi: authApiMocks }));

import LoginView from "@/views/LoginView.vue";
import { useAuth } from "@/composables/useAuth.js";
import { ApiError } from "@/services/http.js";
import { crearRouter } from "../../helpers/router.js";

const montar = async (path = "/login") => {
  useAuth().clearSession();
  const router = await crearRouter(path);
  const wrapper = mount(LoginView, { global: { plugins: [router] } });
  return { wrapper, router };
};

const rellenar = async (wrapper, email = "ana@demo.com", password = "Usuario123") => {
  await wrapper.find('[data-test="login-email"]').setValue(email);
  await wrapper.find('[data-test="login-password"]').setValue(password);
};

describe("LoginView", () => {
  beforeEach(() => {
    useAuth().clearSession();
  });

  it("con un email inválido muestra el error sin llamar a la API", async () => {
    const { wrapper } = await montar();
    await rellenar(wrapper, "correo-invalido", "Usuario123");

    await wrapper.find('[data-test="login-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="login-email-error"]').text()).toBe("El email no tiene un formato válido");
    expect(authApiMocks.login).not.toHaveBeenCalled();
  });

  it("con la contraseña vacía muestra el error y no llama a la API", async () => {
    const { wrapper } = await montar();
    await rellenar(wrapper, "ana@demo.com", "");

    await wrapper.find('[data-test="login-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="login-password-error"]').text()).toBe("La contraseña es obligatoria");
    expect(authApiMocks.login).not.toHaveBeenCalled();
  });

  it("con credenciales incorrectas muestra el alert del servidor y limpia la contraseña", async () => {
    authApiMocks.login.mockRejectedValue(new ApiError(401, "Credenciales inválidas"));
    const { wrapper } = await montar();
    await rellenar(wrapper, "ana@demo.com", "Incorrecta123");

    await wrapper.find('[data-test="login-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="alert"]').text()).toBe("Credenciales inválidas");
    expect(wrapper.find('[data-test="login-password"]').element.value).toBe("");
  });

  it("con credenciales correctas inicia sesión y vuelve al destino de redirect", async () => {
    authApiMocks.login.mockResolvedValue({
      token: "token",
      usuario: { uid: "1", nombre: "Ana", email: "ana@demo.com", rol: "usuario" },
    });
    const { wrapper, router } = await montar("/login?redirect=/perfil");
    await rellenar(wrapper);

    await wrapper.find('[data-test="login-form"]').trigger("submit");
    await flushPromises();

    expect(authApiMocks.login).toHaveBeenCalledWith({ email: "ana@demo.com", password: "Usuario123" });
    expect(router.currentRoute.value.fullPath).toBe("/perfil");
  });

  it("ignora un redirect externo y navega al inicio", async () => {
    authApiMocks.login.mockResolvedValue({
      token: "token",
      usuario: { uid: "1", nombre: "Ana", email: "ana@demo.com", rol: "usuario" },
    });
    const { wrapper, router } = await montar("/login?redirect=//evil.com");
    await rellenar(wrapper);

    await wrapper.find('[data-test="login-form"]').trigger("submit");
    await flushPromises();

    expect(router.currentRoute.value.fullPath).toBe("/");
  });
});

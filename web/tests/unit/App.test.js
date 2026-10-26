import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

const authApiMocks = vi.hoisted(() => ({
  login: vi.fn(),
  registro: vi.fn(),
  perfil: vi.fn(),
  actualizarPerfil: vi.fn(),
  cambiarPassword: vi.fn(),
}));

vi.mock("@/services/authApi.js", () => ({ authApi: authApiMocks }));

import App from "@/App.vue";
import { useAuth } from "@/composables/useAuth.js";
import { useToast } from "@/composables/useToast.js";
import { crearRouter } from "../helpers/router.js";

const montar = async (usuario) => {
  const auth = useAuth();
  auth.clearSession();
  if (usuario) {
    authApiMocks.login.mockResolvedValue({ token: "token", usuario });
    await auth.login({});
  }
  const router = await crearRouter("/login");
  return mount(App, { global: { plugins: [router] } });
};

describe("App", () => {
  beforeEach(() => {
    useAuth().clearSession();
    const { toasts, dismiss } = useToast();
    toasts.slice().forEach((toast) => dismiss(toast.id));
  });

  it("sin sesión no muestra el encabezado y centra el contenido", async () => {
    const wrapper = await montar(null);

    expect(wrapper.find("header").exists()).toBe(false);
    expect(wrapper.find(".layout__content--centered").exists()).toBe(true);
  });

  it("con sesión muestra el encabezado y el contenedor de toasts", async () => {
    const wrapper = await montar({
      uid: "1",
      nombre: "Ana Torres",
      email: "ana@demo.com",
      rol: "usuario",
    });

    expect(wrapper.find("header").exists()).toBe(true);
    expect(wrapper.find(".toasts").exists()).toBe(true);
  });
});

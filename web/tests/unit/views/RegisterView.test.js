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

import RegisterView from "@/views/RegisterView.vue";
import { useAuth } from "@/composables/useAuth.js";
import { useToast } from "@/composables/useToast.js";
import { ApiError } from "@/services/http.js";
import { crearRouter } from "../../helpers/router.js";

const montar = async () => {
  useAuth().clearSession();
  const router = await crearRouter("/registro");
  const wrapper = mount(RegisterView, { global: { plugins: [router] } });
  return { wrapper, router };
};

const rellenar = async (wrapper, overrides = {}) => {
  const datos = {
    nombre: "Nueva Persona",
    email: "nueva@demo.com",
    password: "Password123",
    confirmation: "Password123",
    ...overrides,
  };
  await wrapper.find('[data-test="register-name"]').setValue(datos.nombre);
  await wrapper.find('[data-test="register-email"]').setValue(datos.email);
  await wrapper.find('[data-test="register-password"]').setValue(datos.password);
  await wrapper.find('[data-test="register-confirmation"]').setValue(datos.confirmation);
};

describe("RegisterView", () => {
  beforeEach(() => {
    useAuth().clearSession();
    const { toasts, dismiss } = useToast();
    toasts.slice().forEach((toast) => dismiss(toast.id));
  });

  it("con contraseñas distintas muestra el error y no llama a la API", async () => {
    const { wrapper } = await montar();
    await rellenar(wrapper, { confirmation: "OtraPassword123" });

    await wrapper.find('[data-test="register-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="register-confirmation-error"]').text()).toBe("Las contraseñas no coinciden");
    expect(authApiMocks.registro).not.toHaveBeenCalled();
  });

  it("muestra los errores por campo que devuelve la API", async () => {
    authApiMocks.registro.mockRejectedValue(
      new ApiError(400, "Revisa los datos del formulario", { email: "Ese email ya está registrado" }),
    );
    const { wrapper } = await montar();
    await rellenar(wrapper);

    await wrapper.find('[data-test="register-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="register-email-error"]').text()).toBe("Ese email ya está registrado");
  });

  it("muestra el error general cuando la API no devuelve detalles por campo", async () => {
    authApiMocks.registro.mockRejectedValue(new ApiError(500, "Error interno"));
    const { wrapper } = await montar();
    await rellenar(wrapper);

    await wrapper.find('[data-test="register-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="alert"]').text()).toBe("Error interno");
  });

  it("al registrarse muestra un toast y navega al inicio", async () => {
    authApiMocks.registro.mockResolvedValue({
      token: "token",
      usuario: { uid: "1", nombre: "Nueva Persona", email: "nueva@demo.com", rol: "usuario" },
    });
    const { wrapper, router } = await montar();
    await rellenar(wrapper);

    await wrapper.find('[data-test="register-form"]').trigger("submit");
    await flushPromises();

    expect(authApiMocks.registro).toHaveBeenCalledWith({
      nombre: "Nueva Persona",
      email: "nueva@demo.com",
      password: "Password123",
    });
    expect(useToast().toasts[0].message).toContain("Cuenta creada");
    expect(router.currentRoute.value.fullPath).toBe("/");
  });
});

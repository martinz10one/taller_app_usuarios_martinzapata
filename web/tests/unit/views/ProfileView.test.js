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

import ProfileView from "@/views/ProfileView.vue";
import { useAuth } from "@/composables/useAuth.js";
import { useToast } from "@/composables/useToast.js";
import { ApiError } from "@/services/http.js";

const USUARIO = {
  uid: "64b000000000000000000001",
  nombre: "Ana Torres",
  email: "ana@demo.com",
  rol: "usuario",
  createdAt: "2025-01-15T12:00:00.000Z",
};

const montar = () => {
  const auth = useAuth();
  auth.clearSession();
  auth.setUser({ ...USUARIO });
  return mount(ProfileView);
};

describe("ProfileView", () => {
  beforeEach(() => {
    useAuth().clearSession();
    const { toasts, dismiss } = useToast();
    toasts.slice().forEach((toast) => dismiss(toast.id));
  });

  it("muestra el rol y los datos del usuario", () => {
    const wrapper = montar();

    expect(wrapper.find('[data-test="profile-role"]').text()).toBe("Usuario");
    expect(wrapper.find('[data-test="profile-name"]').element.value).toBe("Ana Torres");
    expect(wrapper.find('[data-test="profile-email"]').element.value).toBe("ana@demo.com");
  });

  it("muestra Administrador cuando el rol es admin", () => {
    const auth = useAuth();
    auth.clearSession();
    auth.setUser({ ...USUARIO, rol: "admin" });
    const wrapper = mount(ProfileView);

    expect(wrapper.find('[data-test="profile-role"]').text()).toBe("Administrador");
  });

  it("guarda los datos personales y actualiza el usuario de la sesión", async () => {
    authApiMocks.actualizarPerfil.mockResolvedValue({ ...USUARIO, nombre: "Ana Actualizada" });
    const wrapper = montar();
    await wrapper.find('[data-test="profile-name"]').setValue("Ana Actualizada");

    await wrapper.find('[data-test="profile-form"]').trigger("submit");
    await flushPromises();

    expect(authApiMocks.actualizarPerfil).toHaveBeenCalledWith({
      nombre: "Ana Actualizada",
      email: "ana@demo.com",
    });
    expect(useAuth().state.user.nombre).toBe("Ana Actualizada");
    expect(useToast().toasts[0].message).toBe("Perfil actualizado");
  });

  it("con un email inválido no llama a la API", async () => {
    const wrapper = montar();
    await wrapper.find('[data-test="profile-email"]').setValue("correo-invalido");

    await wrapper.find('[data-test="profile-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="profile-email-error"]').text()).toBe("El email no tiene un formato válido");
    expect(authApiMocks.actualizarPerfil).not.toHaveBeenCalled();
  });

  it("muestra los detalles por campo que devuelve la API al guardar el perfil", async () => {
    authApiMocks.actualizarPerfil.mockRejectedValue(
      new ApiError(400, "Revisa los datos del formulario", { email: "Ese email ya está registrado" }),
    );
    const wrapper = montar();

    await wrapper.find('[data-test="profile-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="profile-email-error"]').text()).toBe("Ese email ya está registrado");
  });

  it("muestra el error general al fallar el guardado sin detalles por campo", async () => {
    authApiMocks.actualizarPerfil.mockRejectedValue(new ApiError(500, "No se pudo guardar el perfil"));
    const wrapper = montar();

    await wrapper.find('[data-test="profile-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="alert"]').text()).toBe("No se pudo guardar el perfil");
  });

  it("cambia la contraseña correctamente y limpia el formulario", async () => {
    authApiMocks.cambiarPassword.mockResolvedValue({ mensaje: "Contraseña actualizada" });
    const wrapper = montar();
    await wrapper.find('[data-test="password-current"]').setValue("Password123");
    await wrapper.find('[data-test="password-new"]').setValue("NuevaPassword123");
    await wrapper.find('[data-test="password-confirmation"]').setValue("NuevaPassword123");

    await wrapper.find('[data-test="password-form"]').trigger("submit");
    await flushPromises();

    expect(authApiMocks.cambiarPassword).toHaveBeenCalledWith({
      passwordActual: "Password123",
      passwordNueva: "NuevaPassword123",
    });
    expect(wrapper.find('[data-test="password-current"]').element.value).toBe("");
    expect(useToast().toasts[0].message).toBe("Contraseña actualizada");
  });

  it("no llama a la API si la nueva contraseña no cumple las reglas", async () => {
    const wrapper = montar();
    await wrapper.find('[data-test="password-current"]').setValue("Password123");
    await wrapper.find('[data-test="password-new"]').setValue("corta");
    await wrapper.find('[data-test="password-confirmation"]').setValue("corta");

    await wrapper.find('[data-test="password-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="password-new-error"]').exists()).toBe(true);
    expect(authApiMocks.cambiarPassword).not.toHaveBeenCalled();
  });

  it("muestra el error general al fallar el cambio de contraseña", async () => {
    authApiMocks.cambiarPassword.mockRejectedValue(new ApiError(400, "La contraseña actual no es correcta"));
    const wrapper = montar();
    await wrapper.find('[data-test="password-current"]').setValue("Incorrecta123");
    await wrapper.find('[data-test="password-new"]').setValue("NuevaPassword123");
    await wrapper.find('[data-test="password-confirmation"]').setValue("NuevaPassword123");

    await wrapper.find('[data-test="password-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="alert"]').text()).toBe("La contraseña actual no es correcta");
  });

  it("muestra el error de passwordNueva devuelto por la API", async () => {
    authApiMocks.cambiarPassword.mockRejectedValue(
      new ApiError(400, "Revisa los datos del formulario", {
        passwordNueva: "La nueva contraseña debe ser distinta de la actual",
      }),
    );
    const wrapper = montar();
    await wrapper.find('[data-test="password-current"]').setValue("Password123");
    await wrapper.find('[data-test="password-new"]').setValue("NuevaPassword123");
    await wrapper.find('[data-test="password-confirmation"]').setValue("NuevaPassword123");

    await wrapper.find('[data-test="password-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="password-new-error"]').text()).toBe(
      "La nueva contraseña debe ser distinta de la actual",
    );
  });
});

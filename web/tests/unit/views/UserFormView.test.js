import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

const usersApiMocks = vi.hoisted(() => ({
  listar: vi.fn(),
  obtener: vi.fn(),
  crear: vi.fn(),
  actualizar: vi.fn(),
  eliminar: vi.fn(),
}));

vi.mock("@/services/usersApi.js", () => ({ usersApi: usersApiMocks }));

import UserFormView from "@/views/UserFormView.vue";
import { useAuth } from "@/composables/useAuth.js";
import { useToast } from "@/composables/useToast.js";
import { ApiError } from "@/services/http.js";
import { crearRouter } from "../../helpers/router.js";

const USUARIO = {
  uid: "64b000000000000000000001",
  nombre: "Ana Torres",
  email: "ana@demo.com",
  rol: "usuario",
  createdAt: "2025-01-15T12:00:00.000Z",
};

const montar = async (props = {}) => {
  const router = await crearRouter(props.id ? `/usuarios/${props.id}/editar` : "/usuarios/nuevo");
  const wrapper = mount(UserFormView, { props, global: { plugins: [router] } });
  return { wrapper, router };
};

describe("UserFormView", () => {
  beforeEach(() => {
    useAuth().clearSession();
    const { toasts, dismiss } = useToast();
    toasts.slice().forEach((toast) => dismiss(toast.id));
  });

  it("en modo creación valida los campos y no llama a la API si faltan datos", async () => {
    const { wrapper } = await montar();

    await wrapper.find('[data-test="user-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="user-name-error"]').text()).toBe("El nombre es obligatorio");
    expect(wrapper.find('[data-test="user-email-error"]').text()).toBe("El email es obligatorio");
    expect(usersApiMocks.crear).not.toHaveBeenCalled();
  });

  it("crea un usuario y vuelve al listado", async () => {
    usersApiMocks.crear.mockResolvedValue({ uid: "nuevo" });
    const { wrapper, router } = await montar();
    await wrapper.find('[data-test="user-name"]').setValue("Nuevo Usuario");
    await wrapper.find('[data-test="user-email"]').setValue("nuevo@demo.com");
    await wrapper.find('[data-test="user-password"]').setValue("Password123");

    await wrapper.find('[data-test="user-form"]').trigger("submit");
    await flushPromises();

    expect(usersApiMocks.crear).toHaveBeenCalledWith({
      nombre: "Nuevo Usuario",
      email: "nuevo@demo.com",
      rol: "usuario",
      password: "Password123",
    });
    expect(useToast().toasts[0].message).toBe("Usuario creado");
    expect(router.currentRoute.value.name).toBe("users");
  });

  it("en modo edición carga los datos y no envía la contraseña vacía", async () => {
    usersApiMocks.obtener.mockResolvedValue(USUARIO);
    usersApiMocks.actualizar.mockResolvedValue({ ...USUARIO, nombre: "Ana Editada" });
    const { wrapper, router } = await montar({ id: USUARIO.uid });
    await flushPromises();

    expect(wrapper.find('[data-test="user-name"]').element.value).toBe("Ana Torres");
    expect(wrapper.find('[data-test="user-email"]').element.value).toBe("ana@demo.com");

    await wrapper.find('[data-test="user-name"]').setValue("Ana Editada");
    await wrapper.find('[data-test="user-form"]').trigger("submit");
    await flushPromises();

    expect(usersApiMocks.actualizar).toHaveBeenCalledWith(USUARIO.uid, {
      nombre: "Ana Editada",
      email: "ana@demo.com",
      rol: "usuario",
    });
    expect(useToast().toasts[0].message).toBe("Usuario actualizado");
    expect(router.currentRoute.value.name).toBe("users");
  });

  it("muestra el estado de usuario no encontrado si la API responde 404", async () => {
    usersApiMocks.obtener.mockRejectedValue(new ApiError(404, "Usuario no encontrado"));
    const { wrapper } = await montar({ id: "64b000000000000000000099" });
    await flushPromises();

    expect(wrapper.find('[data-test="user-not-found"]').exists()).toBe(true);
  });

  it("muestra el error general si al cargar el usuario la API falla con 500", async () => {
    usersApiMocks.obtener.mockRejectedValue(new ApiError(500, "Error interno"));
    const { wrapper } = await montar({ id: "64b000000000000000000099" });
    await flushPromises();

    expect(wrapper.find('[data-test="alert"]').text()).toBe("Error interno");
    expect(wrapper.find('[data-test="user-not-found"]').exists()).toBe(false);
  });

  it("deshabilita el rol y muestra la pista cuando un admin se edita a sí mismo", async () => {
    useAuth().setUser({ ...USUARIO, rol: "admin" });
    usersApiMocks.obtener.mockResolvedValue({ ...USUARIO, rol: "admin" });
    const { wrapper } = await montar({ id: USUARIO.uid });
    await flushPromises();

    expect(wrapper.find('[data-test="user-role"]').attributes("disabled")).toBeDefined();
    expect(wrapper.find('[data-test="self-edit-hint"]').exists()).toBe(true);
  });

  it("muestra los errores por campo y el error general de la API", async () => {
    usersApiMocks.crear.mockRejectedValue(
      new ApiError(400, "Revisa los datos del formulario", { email: "Ese email ya está registrado" }),
    );
    const { wrapper } = await montar();
    await wrapper.find('[data-test="user-name"]').setValue("Nuevo Usuario");
    await wrapper.find('[data-test="user-email"]').setValue("ocupado@demo.com");
    await wrapper.find('[data-test="user-password"]').setValue("Password123");

    await wrapper.find('[data-test="user-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="user-email-error"]').text()).toBe("Ese email ya está registrado");
  });

  it("muestra el alert general cuando el error no trae detalles por campo", async () => {
    usersApiMocks.crear.mockRejectedValue(new ApiError(500, "Error interno"));
    const { wrapper } = await montar();
    await wrapper.find('[data-test="user-name"]').setValue("Nuevo Usuario");
    await wrapper.find('[data-test="user-email"]').setValue("nuevo@demo.com");
    await wrapper.find('[data-test="user-password"]').setValue("Password123");

    await wrapper.find('[data-test="user-form"]').trigger("submit");
    await flushPromises();

    expect(wrapper.find('[data-test="alert"]').text()).toBe("Error interno");
  });
});

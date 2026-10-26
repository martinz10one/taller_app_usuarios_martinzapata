import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it } from "vitest";
import AppHeader from "@/components/AppHeader.vue";
import { useAuth } from "@/composables/useAuth.js";
import { crearRouter } from "../../helpers/router.js";

const montar = async (usuario) => {
  const auth = useAuth();
  auth.clearSession();
  if (usuario) auth.setUser(usuario);

  const router = await crearRouter("/perfil");
  const wrapper = mount(AppHeader, { global: { plugins: [router] } });
  return { wrapper, router, auth };
};

const ADMIN = { uid: "1", nombre: "Marta Ruiz", email: "marta@demo.com", rol: "admin" };
const USUARIO = { uid: "2", nombre: "Ana Torres", email: "ana@demo.com", rol: "usuario" };

describe("AppHeader", () => {
  beforeEach(() => {
    useAuth().clearSession();
  });

  it("muestra el nombre, las iniciales y el enlace Usuarios para un admin", async () => {
    const { wrapper } = await montar(ADMIN);

    expect(wrapper.find('[data-test="current-user-name"]').text()).toBe("Marta Ruiz");
    expect(wrapper.find(".avatar").text()).toBe("MR");
    expect(wrapper.find('[data-test="nav-users"]').exists()).toBe(true);
    expect(wrapper.text()).toContain("Administrador");
  });

  it("un usuario normal no ve el enlace Usuarios", async () => {
    const { wrapper } = await montar(USUARIO);

    expect(wrapper.find('[data-test="nav-users"]').exists()).toBe(false);
    expect(wrapper.find('[data-test="nav-profile"]').exists()).toBe(true);
    expect(wrapper.text()).toContain("Usuario");
  });

  it("cerrar sesión limpia el usuario y navega al login", async () => {
    const { wrapper, router, auth } = await montar(ADMIN);

    await wrapper.find('[data-test="logout"]').trigger("click");
    await flushPromises();

    expect(auth.state.user).toBeNull();
    expect(router.currentRoute.value.name).toBe("login");
  });

  it("el botón del menú cambia aria-expanded al pulsarlo", async () => {
    const { wrapper } = await montar(USUARIO);
    const toggle = wrapper.find(".header__toggle");

    expect(toggle.attributes("aria-expanded")).toBe("false");
    await toggle.trigger("click");
    expect(toggle.attributes("aria-expanded")).toBe("true");
  });
});

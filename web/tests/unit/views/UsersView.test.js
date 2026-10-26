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

import UsersView from "@/views/UsersView.vue";
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import { useAuth } from "@/composables/useAuth.js";
import { useToast } from "@/composables/useToast.js";
import { ApiError } from "@/services/http.js";
import { crearRouter } from "../../helpers/router.js";

const ANA = {
  uid: "64b000000000000000000001",
  nombre: "Ana Torres",
  email: "ana@demo.com",
  rol: "usuario",
  createdAt: "2025-01-15T12:00:00.000Z",
};
const LUIS = {
  uid: "64b000000000000000000002",
  nombre: "Luis Gómez",
  email: "luis@demo.com",
  rol: "usuario",
  createdAt: "2025-01-16T12:00:00.000Z",
};

const respuesta = (overrides = {}) => ({
  usuarios: [ANA, LUIS],
  total: 2,
  pagina: 1,
  limite: 8,
  totalPaginas: 1,
  ...overrides,
});

const montar = async (path = "/usuarios") => {
  const router = await crearRouter(path);
  const wrapper = mount(UsersView, { global: { plugins: [router] } });
  await flushPromises();
  return { wrapper, router };
};

describe("UsersView", () => {
  beforeEach(() => {
    useAuth().clearSession();
    useAuth().setUser({ uid: "admin-1", nombre: "Admin", email: "admin@demo.com", rol: "admin" });
    const { toasts, dismiss } = useToast();
    toasts.slice().forEach((toast) => dismiss(toast.id));
  });

  it("muestra el total y una fila por usuario", async () => {
    usersApiMocks.listar.mockResolvedValue(respuesta());
    const { wrapper } = await montar();

    expect(wrapper.find('[data-test="users-total"]').text()).toBe("2 usuarios activos");
    expect(wrapper.findAll('[data-test="user-row"]')).toHaveLength(2);
    expect(wrapper.text()).toContain("Ana Torres");
    expect(wrapper.text()).toContain("Luis Gómez");
  });

  it("muestra el estado vacío cuando no hay usuarios", async () => {
    usersApiMocks.listar.mockResolvedValue(respuesta({ usuarios: [], total: 0, totalPaginas: 1 }));
    const { wrapper } = await montar();

    expect(wrapper.find('[data-test="users-empty"]').text()).toBe("Todavía no hay usuarios.");
  });

  it("muestra un mensaje distinto cuando hay filtros sin resultados", async () => {
    usersApiMocks.listar.mockResolvedValue(respuesta({ usuarios: [], total: 0, totalPaginas: 1 }));
    const { wrapper } = await montar("/usuarios?buscar=zzz");

    expect(wrapper.find('[data-test="users-empty"]').text()).toBe("Ningún usuario coincide con los filtros.");
  });

  it("muestra el error y permite reintentar", async () => {
    usersApiMocks.listar.mockRejectedValueOnce(new ApiError(500, "Error interno"));
    const { wrapper } = await montar();

    expect(wrapper.find('[data-test="alert"]').text()).toBe("Error interno");
    expect(wrapper.find('[data-test="users-retry"]').exists()).toBe(true);

    usersApiMocks.listar.mockResolvedValue(respuesta());
    await wrapper.find('[data-test="users-retry"]').trigger("click");
    await flushPromises();

    expect(usersApiMocks.listar).toHaveBeenCalledTimes(2);
    expect(wrapper.findAll('[data-test="user-row"]')).toHaveLength(2);
  });

  it("al eliminar pide confirmación y luego recarga el listado", async () => {
    usersApiMocks.listar.mockResolvedValue(respuesta());
    usersApiMocks.eliminar.mockResolvedValue({ mensaje: "Usuario eliminado" });
    const { wrapper } = await montar();

    await wrapper.find('[data-test="user-delete"]').trigger("click");
    expect(wrapper.findComponent(ConfirmDialog).props("open")).toBe(true);

    document.querySelector('[data-test="confirm-accept"]').click();
    await flushPromises();

    expect(usersApiMocks.eliminar).toHaveBeenCalledWith(ANA.uid);
    expect(useToast().toasts[0].message).toContain("Ana Torres");
    expect(usersApiMocks.listar).toHaveBeenCalledTimes(2);
  });

  it("no permite eliminar la propia cuenta del admin", async () => {
    useAuth().clearSession();
    useAuth().setUser({ ...ANA, rol: "admin" });
    usersApiMocks.listar.mockResolvedValue(respuesta());
    const { wrapper } = await montar();

    const boton = wrapper.findAll('[data-test="user-delete"]')[0];
    expect(boton.attributes("disabled")).toBeDefined();
  });

  it("al cambiar de página actualiza la query y vuelve a listar", async () => {
    usersApiMocks.listar.mockResolvedValue(respuesta({ total: 10, totalPaginas: 2 }));
    const { wrapper, router } = await montar();

    await wrapper.find('[data-test="pagination-next"]').trigger("click");
    await flushPromises();

    expect(router.currentRoute.value.query.pagina).toBe("2");
    expect(usersApiMocks.listar).toHaveBeenLastCalledWith(
      expect.objectContaining({ pagina: 2, limite: 8 }),
    );
  });

  it("al cambiar el filtro de rol actualiza la query y lista con ese rol", async () => {
    usersApiMocks.listar.mockResolvedValue(respuesta());
    const { wrapper, router } = await montar();

    await wrapper.find('[data-test="users-role-filter"]').setValue("admin");
    await flushPromises();

    expect(router.currentRoute.value.query.rol).toBe("admin");
    expect(usersApiMocks.listar).toHaveBeenLastCalledWith(expect.objectContaining({ rol: "admin" }));
  });

  it("la búsqueda espera el debounce antes de actualizar la query", async () => {
    usersApiMocks.listar.mockResolvedValue(respuesta());
    const { wrapper, router } = await montar();

    await wrapper.find('[data-test="users-search"]').setValue("ana");
    await new Promise((resolve) => setTimeout(resolve, 350));
    await flushPromises();

    expect(router.currentRoute.value.query.buscar).toBe("ana");
    expect(usersApiMocks.listar).toHaveBeenLastCalledWith(expect.objectContaining({ buscar: "ana" }));
  });

  it("limpiar filtros borra la query y el buscador", async () => {
    usersApiMocks.listar.mockResolvedValue(respuesta());
    const { wrapper, router } = await montar("/usuarios?buscar=ana");

    await wrapper.find('[data-test="users-clear-filters"]').trigger("click");
    await flushPromises();

    expect(router.currentRoute.value.query).toEqual({});
    expect(wrapper.find('[data-test="users-search"]').element.value).toBe("");
  });

  it("si la última página queda vacía retrocede a la página anterior", async () => {
    usersApiMocks.listar
      .mockResolvedValueOnce(respuesta({ usuarios: [], total: 1, pagina: 2, totalPaginas: 2 }))
      .mockResolvedValue(respuesta({ usuarios: [ANA], total: 1, pagina: 1, totalPaginas: 1 }));

    const { wrapper, router } = await montar("/usuarios?pagina=2");
    await flushPromises();

    expect(router.currentRoute.value.query.pagina).toBe("1");
    expect(usersApiMocks.listar).toHaveBeenLastCalledWith(expect.objectContaining({ pagina: 1 }));
    expect(wrapper.findAll('[data-test="user-row"]')).toHaveLength(1);
  });

  it("si falla la eliminación muestra un toast de error y no recarga el listado", async () => {
    usersApiMocks.listar.mockResolvedValue(respuesta());
    usersApiMocks.eliminar.mockRejectedValue(new ApiError(500, "Error interno"));
    const { wrapper } = await montar();

    await wrapper.find('[data-test="user-delete"]').trigger("click");
    document.querySelector('[data-test="confirm-accept"]').click();
    await flushPromises();

    expect(usersApiMocks.eliminar).toHaveBeenCalledWith(ANA.uid);
    expect(useToast().toasts[0]).toMatchObject({ message: "Error interno", type: "error" });
    expect(usersApiMocks.listar).toHaveBeenCalledTimes(1);
  });
});

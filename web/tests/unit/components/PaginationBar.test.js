import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import PaginationBar from "@/components/PaginationBar.vue";

const montar = (props = {}) =>
  mount(PaginationBar, { props: { page: 1, totalPages: 3, total: 20, limit: 8, ...props } });

describe("PaginationBar", () => {
  it("en la página 1 muestra el rango y deshabilita Anterior", () => {
    const wrapper = montar();

    expect(wrapper.find('[data-test="pagination-info"]').text()).toContain("Mostrando 1–8 de 20");
    expect(wrapper.find('[data-test="pagination-prev"]').attributes("disabled")).toBeDefined();
    expect(wrapper.find('[data-test="pagination-next"]').attributes("disabled")).toBeUndefined();
  });

  it("emite change con la página siguiente al pulsar Siguiente", async () => {
    const wrapper = montar();

    await wrapper.find('[data-test="pagination-next"]').trigger("click");

    expect(wrapper.emitted("change")[0]).toEqual([2]);
  });

  it("en la última página deshabilita Siguiente y emite la anterior", async () => {
    const wrapper = montar({ page: 3 });

    expect(wrapper.find('[data-test="pagination-next"]').attributes("disabled")).toBeDefined();
    expect(wrapper.find('[data-test="pagination-info"]').text()).toContain("Mostrando 17–20 de 20");

    await wrapper.find('[data-test="pagination-prev"]').trigger("click");
    expect(wrapper.emitted("change")[0]).toEqual([2]);
  });

  it("con total 0 muestra 0–0 y ambos botones deshabilitados", () => {
    const wrapper = montar({ page: 1, totalPages: 1, total: 0 });

    expect(wrapper.find('[data-test="pagination-info"]').text()).toContain("Mostrando 0–0 de 0");
    expect(wrapper.find('[data-test="pagination-prev"]').attributes("disabled")).toBeDefined();
    expect(wrapper.find('[data-test="pagination-next"]').attributes("disabled")).toBeDefined();
  });

  it("muestra el número de página y el total de páginas", () => {
    const wrapper = montar({ page: 2 });
    expect(wrapper.find('[data-test="pagination-page"]').text()).toBe("Página 2 de 3");
  });
});

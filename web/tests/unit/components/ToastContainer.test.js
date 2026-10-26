import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it } from "vitest";
import ToastContainer from "@/components/ToastContainer.vue";
import { useToast } from "@/composables/useToast.js";

describe("ToastContainer", () => {
  beforeEach(() => {
    const { toasts, dismiss } = useToast();
    toasts.slice().forEach((toast) => dismiss(toast.id));
  });

  it("muestra los toasts activos", () => {
    useToast().success("Perfil actualizado");
    useToast().error("No se pudo guardar");

    const wrapper = mount(ToastContainer);

    expect(wrapper.findAll('[data-test="toast"]')).toHaveLength(2);
    expect(wrapper.text()).toContain("Perfil actualizado");
    expect(wrapper.text()).toContain("No se pudo guardar");
  });

  it("el botón de cerrar elimina el toast", async () => {
    useToast().success("Temporal");
    const wrapper = mount(ToastContainer);

    await wrapper.find(".toast__close").trigger("click");

    expect(wrapper.findAll('[data-test="toast"]')).toHaveLength(0);
  });
});

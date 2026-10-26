import { nextTick } from "vue";
import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, it } from "vitest";
import ConfirmDialog from "@/components/ConfirmDialog.vue";

const montar = (props = {}) =>
  mount(ConfirmDialog, {
    props: { open: true, title: "Eliminar usuario", message: "No se puede deshacer", ...props },
    attachTo: document.body,
  });

afterEach(() => {
  document.body.innerHTML = "";
});

describe("ConfirmDialog", () => {
  it("no renderiza el diálogo cuando open es false", () => {
    montar({ open: false });
    expect(document.querySelector('[data-test="confirm-dialog"]')).toBeNull();
  });

  it("muestra el título y el mensaje cuando está abierto", () => {
    montar();
    expect(document.body.textContent).toContain("Eliminar usuario");
    expect(document.body.textContent).toContain("No se puede deshacer");
  });

  it("emite confirm al pulsar confirm-accept", async () => {
    const wrapper = montar();

    document.querySelector('[data-test="confirm-accept"]').click();
    await nextTick();

    expect(wrapper.emitted("confirm")).toHaveLength(1);
  });

  it("emite cancel al pulsar confirm-cancel", async () => {
    const wrapper = montar();

    document.querySelector('[data-test="confirm-cancel"]').click();
    await nextTick();

    expect(wrapper.emitted("cancel")).toHaveLength(1);
  });

  it("con loading deshabilita los botones y muestra Procesando", () => {
    montar({ loading: true });

    const aceptar = document.querySelector('[data-test="confirm-accept"]');
    const cancelar = document.querySelector('[data-test="confirm-cancel"]');

    expect(aceptar.disabled).toBe(true);
    expect(cancelar.disabled).toBe(true);
    expect(aceptar.textContent).toContain("Procesando");
  });

  it("emite cancel al presionar Escape", async () => {
    const wrapper = montar();
    const dialogo = document.querySelector('[data-test="confirm-dialog"]');

    dialogo.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    await nextTick();

    expect(wrapper.emitted("cancel")).toHaveLength(1);
  });
});

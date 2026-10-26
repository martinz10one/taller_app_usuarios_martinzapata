import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import AlertMessage from "@/components/AlertMessage.vue";

describe("AlertMessage", () => {
  it("no renderiza nada si no hay mensaje", () => {
    const wrapper = mount(AlertMessage, { props: { message: "" } });
    expect(wrapper.find('[data-test="alert"]').exists()).toBe(false);
  });

  it("muestra el mensaje con el rol de alerta", () => {
    const wrapper = mount(AlertMessage, { props: { message: "Credenciales inválidas" } });
    const alert = wrapper.find('[data-test="alert"]');

    expect(alert.text()).toBe("Credenciales inválidas");
    expect(alert.attributes("role")).toBe("alert");
    expect(alert.classes()).toContain("alert--error");
  });

  it("aplica la clase del tipo indicado", () => {
    const wrapper = mount(AlertMessage, { props: { message: "Listo", type: "success" } });
    expect(wrapper.find('[data-test="alert"]').classes()).toContain("alert--success");
  });
});

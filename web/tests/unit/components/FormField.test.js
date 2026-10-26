import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import FormField from "@/components/FormField.vue";

const montar = (props = {}) =>
  mount(FormField, {
    props: { label: "Contraseña", modelValue: "", testId: "login-password", ...props },
  });

describe("FormField", () => {
  it("muestra la etiqueta y asigna el data-test al input", () => {
    const wrapper = montar();

    expect(wrapper.text()).toContain("Contraseña");
    expect(wrapper.find('[data-test="login-password"]').exists()).toBe(true);
  });

  it("muestra el error con data-test {testId}-error", () => {
    const wrapper = montar({ error: "La contraseña es obligatoria" });

    expect(wrapper.find('[data-test="login-password-error"]').text()).toBe("La contraseña es obligatoria");
    expect(wrapper.find("input").attributes("aria-invalid")).toBe("true");
  });

  it("muestra el hint cuando no hay error", () => {
    const wrapper = montar({ type: "text", hint: "Mínimo 8 caracteres" });

    expect(wrapper.text()).toContain("Mínimo 8 caracteres");
    expect(wrapper.find('[data-test="login-password-error"]').exists()).toBe(false);
  });

  it("el botón Mostrar/Ocultar cambia el tipo del input", async () => {
    const wrapper = montar({ type: "password" });
    const input = wrapper.find("input");
    const toggle = wrapper.find('[data-test="login-password-toggle"]');

    expect(input.attributes("type")).toBe("password");
    expect(toggle.text()).toBe("Mostrar");

    await toggle.trigger("click");
    expect(input.attributes("type")).toBe("text");
    expect(toggle.text()).toBe("Ocultar");

    await toggle.trigger("click");
    expect(input.attributes("type")).toBe("password");
  });

  it("no muestra botón de revelar si no es un campo de contraseña", () => {
    const wrapper = montar({ type: "email" });
    expect(wrapper.find('[data-test="login-password-toggle"]').exists()).toBe(false);
  });

  it("emite update:modelValue al escribir", async () => {
    const wrapper = montar();

    await wrapper.find("input").setValue("Password123");

    expect(wrapper.emitted("update:modelValue")).toEqual([["Password123"]]);
  });

  it("respeta el estado disabled", () => {
    const wrapper = montar({ disabled: true });
    expect(wrapper.find("input").attributes("disabled")).toBeDefined();
  });
});

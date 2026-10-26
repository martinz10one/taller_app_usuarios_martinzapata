import { beforeEach, describe, expect, it, vi } from "vitest";
import { useToast } from "@/composables/useToast.js";

describe("useToast", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    const { toasts, dismiss } = useToast();
    toasts.slice().forEach((toast) => dismiss(toast.id));
  });

  it("success agrega un toast y lo elimina a los 3500 ms", () => {
    const { toasts, success } = useToast();

    success("Guardado");

    expect(toasts).toHaveLength(1);
    expect(toasts[0]).toMatchObject({ message: "Guardado", type: "success" });

    vi.advanceTimersByTime(3499);
    expect(toasts).toHaveLength(1);

    vi.advanceTimersByTime(1);
    expect(toasts).toHaveLength(0);
  });

  it("error agrega un toast de error y dura 5000 ms", () => {
    const { toasts, error } = useToast();

    error("Falló la operación");

    expect(toasts[0]).toMatchObject({ message: "Falló la operación", type: "error" });

    vi.advanceTimersByTime(4999);
    expect(toasts).toHaveLength(1);

    vi.advanceTimersByTime(1);
    expect(toasts).toHaveLength(0);
  });

  it("dismiss elimina un toast antes de que termine el tiempo", () => {
    const { toasts, success, dismiss } = useToast();

    const id = success("Temporal");
    expect(toasts).toHaveLength(1);

    dismiss(id);
    expect(toasts).toHaveLength(0);
  });

  it("permite varios toasts simultáneos y elimina solo el indicado", () => {
    const { toasts, success, error, dismiss } = useToast();

    const primero = success("Uno");
    success("Dos");
    error("Tres");
    expect(toasts.map((toast) => toast.message)).toEqual(["Uno", "Dos", "Tres"]);

    dismiss(primero);
    expect(toasts.map((toast) => toast.message)).toEqual(["Dos", "Tres"]);
  });

  it("dismiss de un id inexistente no cambia la lista", () => {
    const { toasts, success, dismiss } = useToast();
    success("Uno");

    expect(() => dismiss(99999)).not.toThrow();
    expect(toasts).toHaveLength(1);
  });
});

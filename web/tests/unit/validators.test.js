import { describe, expect, it } from "vitest";
import {
  isValid,
  validateEmail,
  validateName,
  validatePassword,
  validatePasswordConfirmation,
} from "@/utils/validators.js";

describe("validateName", () => {
  it("rechaza un nombre vacío", () => {
    expect(validateName("")).toBe("El nombre es obligatorio");
    expect(validateName("   ")).toBe("El nombre es obligatorio");
  });

  it("rechaza un nombre de un solo carácter", () => {
    expect(validateName("A")).toBe("El nombre debe tener entre 2 y 60 caracteres");
  });

  it("rechaza un nombre de más de 60 caracteres", () => {
    expect(validateName("A".repeat(61))).toBe("El nombre debe tener entre 2 y 60 caracteres");
  });

  it("acepta un nombre válido con espacios alrededor", () => {
    expect(validateName("  Ana Torres  ")).toBe("");
  });
});

describe("validateEmail", () => {
  it("rechaza un email vacío", () => {
    expect(validateEmail("")).toBe("El email es obligatorio");
  });

  it("rechaza un email sin formato válido", () => {
    expect(validateEmail("correo-invalido")).toBe("El email no tiene un formato válido");
    expect(validateEmail("ana@demo")).toBe("El email no tiene un formato válido");
  });

  it("acepta un email válido", () => {
    expect(validateEmail("ana@demo.com")).toBe("");
  });
});

describe("validatePassword", () => {
  it("rechaza una contraseña vacía", () => {
    expect(validatePassword("")).toBe("La contraseña es obligatoria");
  });

  it("rechaza una contraseña corta", () => {
    expect(validatePassword("Ab1")).toBe("La contraseña debe tener entre 8 y 64 caracteres");
  });

  it("rechaza una contraseña de más de 64 caracteres", () => {
    expect(validatePassword(`A1${"a".repeat(64)}`)).toBe(
      "La contraseña debe tener entre 8 y 64 caracteres",
    );
  });

  it("rechaza una contraseña sin mayúscula", () => {
    expect(validatePassword("password123")).toBe("La contraseña debe incluir al menos una mayúscula");
  });

  it("rechaza una contraseña sin minúscula", () => {
    expect(validatePassword("PASSWORD123")).toBe("La contraseña debe incluir al menos una minúscula");
  });

  it("rechaza una contraseña sin número", () => {
    expect(validatePassword("Password")).toBe("La contraseña debe incluir al menos un número");
  });

  it("acepta una contraseña que cumple todas las reglas", () => {
    expect(validatePassword("Password123")).toBe("");
  });
});

describe("validatePasswordConfirmation", () => {
  it("rechaza una confirmación vacía", () => {
    expect(validatePasswordConfirmation("Password123", "")).toBe("Repite la contraseña");
  });

  it("rechaza contraseñas distintas", () => {
    expect(validatePasswordConfirmation("Password123", "Password456")).toBe("Las contraseñas no coinciden");
  });

  it("acepta contraseñas iguales", () => {
    expect(validatePasswordConfirmation("Password123", "Password123")).toBe("");
  });
});

describe("isValid", () => {
  it("devuelve true cuando no hay mensajes", () => {
    expect(isValid({ nombre: "", email: "" })).toBe(true);
  });

  it("devuelve false cuando algún campo tiene mensaje", () => {
    expect(isValid({ nombre: "", email: "Error" })).toBe(false);
  });
});

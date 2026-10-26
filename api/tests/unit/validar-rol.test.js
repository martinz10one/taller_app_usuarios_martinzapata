import { describe, expect, it, vi } from "vitest";
import { validarRol } from "../../middlewares/validar-rol.js";

const crearRes = () => {
  const res = {};
  res.status = vi.fn().mockReturnValue(res);
  res.json = vi.fn().mockReturnValue(res);
  return res;
};

describe("middleware validarRol", () => {
  it("responde 500 si validarJWT no se ejecutó antes", () => {
    const req = {};
    const res = crearRes();
    const next = vi.fn();

    validarRol("admin")(req, res, next);

    expect(res.status).toHaveBeenCalledWith(500);
    expect(res.json).toHaveBeenCalledWith({ error: "Se requiere validarJWT primero" });
    expect(next).not.toHaveBeenCalled();
  });

  it("responde 403 si el rol autenticado no está permitido", () => {
    const req = { usuario: { rol: "usuario" } };
    const res = crearRes();
    const next = vi.fn();

    validarRol("admin")(req, res, next);

    expect(res.status).toHaveBeenCalledWith(403);
    expect(res.json).toHaveBeenCalledWith({ error: "No tiene permisos para esto" });
    expect(next).not.toHaveBeenCalled();
  });

  it("llama a next() cuando el rol está permitido", () => {
    const req = { usuario: { rol: "admin" } };
    const res = crearRes();
    const next = vi.fn();

    validarRol("admin")(req, res, next);

    expect(next).toHaveBeenCalledOnce();
    expect(res.status).not.toHaveBeenCalled();
  });

  it("acepta varios roles permitidos", () => {
    const next = vi.fn();
    validarRol("admin", "usuario")({ usuario: { rol: "usuario" } }, crearRes(), next);
    expect(next).toHaveBeenCalledOnce();
  });
});

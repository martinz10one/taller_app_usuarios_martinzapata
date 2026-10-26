import { describe, expect, it, vi } from "vitest";
import jwt from "jsonwebtoken";
import { validarJWT } from "../../middlewares/validar-jwt.js";
import { generarJWT } from "../../helpers/generar-jwt.js";
import { crearUsuario } from "../helpers.js";

const crearRes = () => {
  const res = {};
  res.status = vi.fn().mockReturnValue(res);
  res.json = vi.fn().mockReturnValue(res);
  return res;
};

const crearReq = (token) => ({ header: vi.fn().mockReturnValue(token) });

describe("middleware validarJWT", () => {
  it("responde 401 si no hay token en la petición", async () => {
    const res = crearRes();
    const next = vi.fn();

    await validarJWT(crearReq(undefined), res, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ error: "No hay token en la petición" });
    expect(next).not.toHaveBeenCalled();
  });

  it("responde 401 si el token es inválido", async () => {
    const res = crearRes();
    const next = vi.fn();

    await validarJWT(crearReq("token-invalido"), res, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ error: "Token no válido o expirado" });
    expect(next).not.toHaveBeenCalled();
  });

  it("responde 401 si el token está firmado con otro secreto", async () => {
    const usuario = await crearUsuario();
    const tokenAjeno = jwt.sign({ uid: usuario.id, rol: usuario.rol }, "otro-secreto");
    const res = crearRes();
    const next = vi.fn();

    await validarJWT(crearReq(tokenAjeno), res, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  it("responde 401 si el usuario fue desactivado", async () => {
    const usuario = await crearUsuario({ estado: false });
    const res = crearRes();
    const next = vi.fn();

    await validarJWT(crearReq(generarJWT(usuario)), res, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ error: "Usuario desactivado" });
    expect(next).not.toHaveBeenCalled();
  });

  it("responde 401 si el usuario del token ya no existe", async () => {
    const usuario = await crearUsuario();
    const token = generarJWT(usuario);
    await usuario.deleteOne();
    const res = crearRes();
    const next = vi.fn();

    await validarJWT(crearReq(token), res, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  it("deja el usuario en req y llama a next() con un token válido", async () => {
    const usuario = await crearUsuario();
    const req = crearReq(generarJWT(usuario));
    const res = crearRes();
    const next = vi.fn();

    await validarJWT(req, res, next);

    expect(req.usuario.id).toBe(usuario.id);
    expect(next).toHaveBeenCalledOnce();
  });
});

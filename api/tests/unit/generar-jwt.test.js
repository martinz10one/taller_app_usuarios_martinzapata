import { describe, expect, it } from "vitest";
import jwt from "jsonwebtoken";
import { generarJWT } from "../../helpers/generar-jwt.js";

describe("generarJWT", () => {
  it("firma un token que contiene uid y rol", () => {
    const token = generarJWT({ id: "64b000000000000000000001", rol: "admin" });
    const payload = jwt.verify(token, process.env.JWT_SECRET);

    expect(payload.uid).toBe("64b000000000000000000001");
    expect(payload.rol).toBe("admin");
    expect(payload.exp).toBeGreaterThan(payload.iat);
  });

  it("genera tokens distintos para usuarios distintos", () => {
    const uno = generarJWT({ id: "64b000000000000000000001", rol: "usuario" });
    const dos = generarJWT({ id: "64b000000000000000000002", rol: "usuario" });
    expect(uno).not.toBe(dos);
  });
});

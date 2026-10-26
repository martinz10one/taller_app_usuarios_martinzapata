import express from "express";
import request from "supertest";
import { check } from "express-validator";
import { describe, expect, it } from "vitest";
import { validarCampos } from "../../middlewares/validar-campos.js";

const app = express();
app.use(express.json());
app.post("/validar", [check("email").isEmail().withMessage("Email no válido"), validarCampos], (req, res) => {
  res.json({ ok: true });
});

describe("middleware validarCampos", () => {
  it("responde 400 con path y mensaje cuando hay errores", async () => {
    const res = await request(app).post("/validar").send({ email: "no-es-un-email" });

    expect(res.status).toBe(400);
    expect(res.body.errores).toEqual([{ path: "email", msg: "Email no válido" }]);
    expect(res.body.errores[0]).not.toHaveProperty("value");
  });

  it("llama al controlador cuando no hay errores", async () => {
    const res = await request(app).post("/validar").send({ email: "valido@test.com" });

    expect(res.status).toBe(200);
    expect(res.body).toEqual({ ok: true });
  });
});

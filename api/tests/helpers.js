import Usuario from "../models/usuario.js";
import { generarJWT } from "../helpers/generar-jwt.js";

let contador = 0;
const emailUnico = (prefijo) => `${prefijo}${++contador}@test.com`;

/**
 * Crea un usuario directamente en la base de pruebas.
 * El email es único aunque no se indique, para evitar colisiones entre pruebas.
 */
export const crearUsuario = async (datos = {}) => {
  const usuario = new Usuario({
    nombre: "Usuario de prueba",
    email: emailUnico("usuario"),
    password: "Password123",
    rol: "usuario",
    ...datos,
  });
  await usuario.save();
  return usuario;
};

export const crearAdmin = (datos = {}) =>
  crearUsuario({ nombre: "Admin de prueba", email: emailUnico("admin"), rol: "admin", ...datos });

/** Token válido para un administrador recién creado. */
export const tokenAdmin = async (datos = {}) => {
  const admin = await crearAdmin(datos);
  return { token: generarJWT(admin), usuario: admin };
};

/** Token válido para un usuario con rol "usuario" recién creado. */
export const tokenUsuario = async (datos = {}) => {
  const usuario = await crearUsuario(datos);
  return { token: generarJWT(usuario), usuario };
};

import { afterAll, afterEach, beforeAll } from "vitest";
import mongoose from "mongoose";
import { MongoMemoryServer } from "mongodb-memory-server";
import Usuario from "../models/usuario.js";

let mongoServer;

beforeAll(async () => {
  // Base de datos real en memoria: nunca se toca la MongoDB de desarrollo.
  mongoServer = await MongoMemoryServer.create();
  process.env.MONGODB_CNX = mongoServer.getUri();

  await mongoose.connect(process.env.MONGODB_CNX);
});

afterEach(async () => {
  // Cada prueba empieza con la colección vacía: no depende del orden.
  await Usuario.deleteMany({});
});

afterAll(async () => {
  await mongoose.disconnect();
  await mongoServer.stop();
});

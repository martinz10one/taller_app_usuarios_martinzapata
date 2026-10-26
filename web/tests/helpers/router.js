import { createMemoryHistory, createRouter } from "vue-router";

const Vacio = { template: "<div />" };

/** Router de prueba con las rutas de la aplicación y componentes vacíos. */
export const crearRouter = async (initialPath = "/") => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", name: "home", component: Vacio },
      { path: "/login", name: "login", component: Vacio },
      { path: "/registro", name: "register", component: Vacio },
      { path: "/perfil", name: "profile", component: Vacio },
      { path: "/usuarios", name: "users", component: Vacio },
      { path: "/usuarios/nuevo", name: "user-create", component: Vacio },
      { path: "/usuarios/:id/editar", name: "user-edit", component: Vacio },
      { path: "/:pathMatch(.*)*", name: "not-found", component: Vacio },
    ],
  });

  await router.push(initialPath);
  await router.isReady();
  return router;
};

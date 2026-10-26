
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** web
- **Date:** 2026-10-26
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001 Iniciar sesión como administrador
- **Test Code:** [TC001_Iniciar_sesin_como_administrador.py](./TC001_Iniciar_sesin_como_administrador.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/28ffb424-be38-4a95-ac0d-26d934d63426
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002 Registrar una cuenta nueva y acceder al destino correcto
- **Test Code:** [TC002_Registrar_una_cuenta_nueva_y_acceder_al_destino_correcto.py](./TC002_Registrar_una_cuenta_nueva_y_acceder_al_destino_correcto.py)
- **Test Error:** TEST FAILURE

El registro no se pudo completar: las distintas direcciones de correo probadas fueron rechazadas como ya registradas. No se alcanzó una sesión autenticada ni se pudo verificar la redirección correspondiente al rol.

Observations:
- El formulario de registro mostró «Ese email ya está registrado» para varias direcciones diferentes.
- El formulario permaneció en la página de registro; no se mostró un destino autenticado.
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/77edc857-ee32-4f9e-945f-61b5bb2864b0
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003 Crear cuenta y entrar al perfil
- **Test Code:** [TC003_Crear_cuenta_y_entrar_al_perfil.py](./TC003_Crear_cuenta_y_entrar_al_perfil.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/92e96f11-a8e6-485f-9fb8-f9e86cb72a9b
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004 Iniciar sesión como usuario normal
- **Test Code:** [TC004_Iniciar_sesin_como_usuario_normal.py](./TC004_Iniciar_sesin_como_usuario_normal.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/dcceb6ca-b0a8-434a-bc0f-a053904ead06
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005 Cerrar sesión y volver al acceso público
- **Test Code:** [TC005_Cerrar_sesin_y_volver_al_acceso_pblico.py](./TC005_Cerrar_sesin_y_volver_al_acceso_pblico.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/bff707e6-c223-4132-8a58-e5f0f0965e5f
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006 Bloquear acceso a usuarios para un usuario normal
- **Test Code:** [TC006_Bloquear_acceso_a_usuarios_para_un_usuario_normal.py](./TC006_Bloquear_acceso_a_usuarios_para_un_usuario_normal.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/50bbb6f9-3ac8-45a8-bc26-eb03c3c3b774
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007 Redirigir a la vista correcta según el rol al entrar
- **Test Code:** [TC007_Redirigir_a_la_vista_correcta_segn_el_rol_al_entrar.py](./TC007_Redirigir_a_la_vista_correcta_segn_el_rol_al_entrar.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/a98a6a69-2baa-4e62-8885-e680f5524de5
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008 Eliminar lógicamente un usuario con confirmación
- **Test Code:** [TC008_Eliminar_lgicamente_un_usuario_con_confirmacin.py](./TC008_Eliminar_lgicamente_un_usuario_con_confirmacin.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/4dc1b414-93c0-45cf-9540-bd7fef8d7c52
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009 Crear un usuario nuevo desde el panel de administración
- **Test Code:** [TC009_Crear_un_usuario_nuevo_desde_el_panel_de_administracin.py](./TC009_Crear_un_usuario_nuevo_desde_el_panel_de_administracin.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/c8ee0b15-f7dc-443c-a202-1f7461ea4153
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC010 Editar un usuario existente desde el panel de administración
- **Test Code:** [TC010_Editar_un_usuario_existente_desde_el_panel_de_administracin.py](./TC010_Editar_un_usuario_existente_desde_el_panel_de_administracin.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/22d939e7-f13e-4113-a080-437628e82e4d
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC011 Editar un usuario existente
- **Test Code:** [TC011_Editar_un_usuario_existente.py](./TC011_Editar_un_usuario_existente.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/e630cdfa-2e4a-488b-a399-c704331372ab
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC012 Bloquear el acceso a usuarios sin permisos
- **Test Code:** [TC012_Bloquear_el_acceso_a_usuarios_sin_permisos.py](./TC012_Bloquear_el_acceso_a_usuarios_sin_permisos.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/c9b04b9b-f895-4980-bf44-fc3304f3d54b
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC013 Buscar usuarios en el listado
- **Test Code:** [TC013_Buscar_usuarios_en_el_listado.py](./TC013_Buscar_usuarios_en_el_listado.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/060e4708-fd0c-49be-a135-548a71a68009
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC014 Buscar y filtrar usuarios desde el panel de administración
- **Test Code:** [TC014_Buscar_y_filtrar_usuarios_desde_el_panel_de_administracin.py](./TC014_Buscar_y_filtrar_usuarios_desde_el_panel_de_administracin.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/3ffc1797-8e0b-4f79-bbda-dcc336acfabc
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC015 Filtrar usuarios por rol
- **Test Code:** [TC015_Filtrar_usuarios_por_rol.py](./TC015_Filtrar_usuarios_por_rol.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/efa4daa1-e6ed-56a8-a635-d7cf46b38892/test/06da11ab-ef85-43a0-9a4e-08fa11d8a0e4
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **93.33** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---
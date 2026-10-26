
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** api
- **Date:** 2026-10-26
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001 post api auth registro create user account
- **Test Code:** [TC001_post_api_auth_registro_create_user_account.py](./TC001_post_api_auth_registro_create_user_account.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/e29c9166-b4ea-4e0d-9cd3-f91a4b89dec6
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002 post api auth login authenticate user
- **Test Code:** [TC002_post_api_auth_login_authenticate_user.py](./TC002_post_api_auth_login_authenticate_user.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/8aef2e80-abae-4fbf-a50c-100d31003280
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003 get api auth perfil get authenticated user profile
- **Test Code:** [TC003_get_api_auth_perfil_get_authenticated_user_profile.py](./TC003_get_api_auth_perfil_get_authenticated_user_profile.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/50b640de-105c-4999-9316-3f71ec979308
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004 put api auth perfil update authenticated user profile
- **Test Code:** [TC004_put_api_auth_perfil_update_authenticated_user_profile.py](./TC004_put_api_auth_perfil_update_authenticated_user_profile.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/901db8d3-bdc0-4e50-bdee-7230178fb424
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005 put api auth password change user password
- **Test Code:** [TC005_put_api_auth_password_change_user_password.py](./TC005_put_api_auth_password_change_user_password.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/bc9df9b9-18be-4c50-8c98-75ffe05b5430
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006 get api usuarios list users with admin role
- **Test Code:** [TC006_get_api_usuarios_list_users_with_admin_role.py](./TC006_get_api_usuarios_list_users_with_admin_role.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/411af12e-c24d-4cba-b470-291c51c87782
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007 get api usuarios id get user details by id
- **Test Code:** [TC007_get_api_usuarios_id_get_user_details_by_id.py](./TC007_get_api_usuarios_id_get_user_details_by_id.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/95b21e0c-91c8-4cd6-8b7c-17644296e71b
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008 post api usuarios create new user by admin
- **Test Code:** [TC008_post_api_usuarios_create_new_user_by_admin.py](./TC008_post_api_usuarios_create_new_user_by_admin.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/b37bf8c0-9210-4c1c-96dc-5282fe1b5c37
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009 put api usuarios id update user details by admin
- **Test Code:** [TC009_put_api_usuarios_id_update_user_details_by_admin.py](./TC009_put_api_usuarios_id_update_user_details_by_admin.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/runner.py", line 234, in run
    ran = _invoke_uncalled_tests(env, called_during_exec)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/task/runner.py", line 87, in _invoke_uncalled_tests
    fn()
  File "<string>", line 122, in test_tc009_put_api_usuarios_id_update_user_details_by_admin
AssertionError: Expected 400 when admin attempts to change own role, got 200: {"uid":"6adfb2ced9a282feb8c09f27","nombre":"Administrador","email":"admin@demo.com","rol":"admin","estado":true,"createdAt":"2026-10-26T20:06:38.642Z","updatedAt":"2026-10-26T20:06:38.642Z"}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/05c52fc4-93ed-4427-ba0d-943f1f646ed0
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC010 delete api usuarios id logical delete user by admin
- **Test Code:** [TC010_delete_api_usuarios_id_logical_delete_user_by_admin.py](./TC010_delete_api_usuarios_id_logical_delete_user_by_admin.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/f31cc8a0-b665-5a6f-959c-42d2579c7531/test/be361980-e9bf-4b5c-802a-620ab0523d93
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **90.00** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---
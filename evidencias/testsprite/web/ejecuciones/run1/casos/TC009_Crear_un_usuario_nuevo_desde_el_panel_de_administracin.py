import asyncio
import re
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None

    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()

        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",
                "--disable-dev-shm-usage",
                "--ipc=host",
                "--single-process"
            ],
        )

        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        # Wider default timeout to match the agent's DOM-stability budget;
        # auto-waiting Playwright APIs (expect, locator.wait_for) inherit this.
        context.set_default_timeout(15000)

        # Open a new page in the browser context
        page = await context.new_page()

        # Interact with the page elements to simulate user flow
        # -> navigate
        await page.goto("http://localhost:5173")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Abrir la ruta de inicio de sesión indicada y comprobar si aparece el formulario de acceso.
        await page.goto("http://localhost:5173/login")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Iniciar sesión usando las credenciales de administrador visibles en la página.
        # tu@email.com email field
        elem = page.locator("[data-test=\"login-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("admin@demo.com")
        
        # -> Iniciar sesión usando las credenciales de administrador visibles en la página.
        # password field
        elem = page.locator("[data-test=\"login-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Admin123!")
        
        # -> Iniciar sesión usando las credenciales de administrador visibles en la página.
        # Entrar button
        elem = page.locator("[data-test=\"login-submit\"]")
        await elem.click(timeout=10000)
        
        # -> Abrir el formulario de alta mediante «+ Nuevo usuario».
        # + Nuevo usuario link
        elem = page.locator("[data-test=\"users-new\"]")
        await elem.click(timeout=10000)
        
        # -> Completar Nombre completo, Email y Contraseña con datos válidos y seleccionar «Crear usuario».
        # text field
        elem = page.locator("[data-test=\"user-name\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Usuario de prueba QA")
        
        # -> Completar Nombre completo, Email y Contraseña con datos válidos y seleccionar «Crear usuario».
        # email field
        elem = page.locator("[data-test=\"user-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("usuario.qa@example.com")
        
        # -> Completar Nombre completo, Email y Contraseña con datos válidos y seleccionar «Crear usuario».
        # password field
        elem = page.locator("[data-test=\"user-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Prueba1234")
        
        # -> Completar Nombre completo, Email y Contraseña con datos válidos y seleccionar «Crear usuario».
        # Crear usuario button
        elem = page.locator("[data-test=\"user-submit\"]")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> El nuevo usuario aparece en el listado de usuarios.
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: El correo del nuevo usuario aparece en el listado.
        await expect(page.locator("xpath=/html/body/div[1]/div/main/section/div/div[2]/table/tbody/tr[8]/td[2]").nth(0)).to_have_text("usuario.qa@example.com", timeout=15000), "El correo del nuevo usuario aparece en el listado."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    
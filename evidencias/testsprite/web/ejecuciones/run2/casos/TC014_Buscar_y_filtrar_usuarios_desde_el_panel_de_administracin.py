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
        
        # -> Iniciar sesión con la cuenta de administrador y comprobar que se abre la interfaz de gestión.
        # tu@email.com email field
        elem = page.locator("[data-test=\"login-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("admin@demo.com")
        
        # -> Iniciar sesión con la cuenta de administrador y comprobar que se abre la interfaz de gestión.
        # password field
        elem = page.locator("[data-test=\"login-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Admin123!")
        
        # -> Iniciar sesión con la cuenta de administrador y comprobar que se abre la interfaz de gestión.
        # Entrar button
        elem = page.locator("[data-test=\"login-submit\"]")
        await elem.click(timeout=10000)
        
        # -> Abrir el listado de usuarios desde el enlace «Usuarios».
        # Usuarios link
        elem = page.locator("[data-test=\"nav-users\"]")
        await elem.click(timeout=10000)
        
        # -> Abrir el listado de usuarios mediante el enlace «Usuarios» y comprobar que aparece su contenido.
        # Usuarios link
        elem = page.locator("[data-test=\"nav-users\"]")
        await elem.click(timeout=10000)
        
        # -> Buscar a Ana Torres usando el campo «Buscar usuarios».
        # Buscar por nombre o email… search field
        elem = page.locator("[data-test=\"users-search\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Ana Torres")
        
        # -> Aplicar el filtro «Usuarios» y verificar el listado filtrado.
        # Todos los roles Administradores Usuarios dropdown
        elem = page.locator("xpath=/html/body/div/div/main/section/div/div/label[2]/select").nth(0)
        await elem.wait_for(state="visible", timeout=10000)
        await elem.select_option("")
        
        # --> Assertions to verify final state
        
        # --> El listado filtrado muestra a Ana Torres.
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: El listado filtrado muestra a Ana Torres.
        await expect(page.locator("[data-test=\"user-row\"]").nth(0)).to_contain_text("Ana Torres", timeout=15000), "El listado filtrado muestra a Ana Torres."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    
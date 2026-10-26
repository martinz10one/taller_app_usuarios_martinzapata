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
        
        # -> Abrir la página de acceso indicada y comprobar si aparece el formulario de inicio de sesión.
        await page.goto("http://localhost:5173/login")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Completar el formulario con las credenciales de administrador visibles y enviar el inicio de sesión.
        # tu@email.com email field
        elem = page.locator("[data-test=\"login-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("admin@demo.com")
        
        # -> Completar el formulario con las credenciales de administrador visibles y enviar el inicio de sesión.
        # password field
        elem = page.locator("[data-test=\"login-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Admin123!")
        
        # -> Completar el formulario con las credenciales de administrador visibles y enviar el inicio de sesión.
        # Entrar button
        elem = page.locator("[data-test=\"login-submit\"]")
        await elem.click(timeout=10000)
        
        # -> Abrir el filtro “Filtrar por rol” para seleccionar un rol y verificar que la tabla muestre solo los usuarios coincidentes.
        # Todos los roles Administradores Usuarios dropdown
        elem = page.locator("[data-test=\"users-role-filter\"]")
        await elem.click(timeout=10000)
        
        # -> Seleccionar «Administradores» en el filtro y comprobar que la lista muestra solo usuarios con ese rol.
        # Todos los roles Administradores Usuarios dropdown
        elem = page.locator("xpath=/html/body/div/div/main/section/div/div/label[2]/select").nth(0)
        await elem.wait_for(state="visible", timeout=10000)
        await elem.select_option("")
        
        # --> Assertions to verify final state
        
        # --> La lista muestra únicamente usuarios con el rol Administrador seleccionado.
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: El primer usuario de la lista tiene el rol Administrador.
        await expect(page.locator("xpath=/html/body/div/div/main/section/div/div[2]/table/tbody/tr[1]/td[3]").nth(0)).to_have_text("Administrador", timeout=15000), "El primer usuario de la lista tiene el rol Administrador."
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: El segundo usuario de la lista tiene el rol Administrador.
        await expect(page.locator("xpath=/html/body/div/div/main/section/div/div[2]/table/tbody/tr[2]/td[3]").nth(0)).to_have_text("Administrador", timeout=15000), "El segundo usuario de la lista tiene el rol Administrador."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    
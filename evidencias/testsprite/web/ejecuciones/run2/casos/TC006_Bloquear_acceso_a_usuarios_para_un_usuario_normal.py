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
        
        # -> Iniciar sesión con la cuenta de prueba de Usuario y revisar la vista permitida que aparece.
        # tu@email.com email field
        elem = page.locator("[data-test=\"login-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("ana@demo.com")
        
        # -> Iniciar sesión con la cuenta de prueba de Usuario y revisar la vista permitida que aparece.
        # password field
        elem = page.locator("[data-test=\"login-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Usuario123")
        
        # -> Iniciar sesión con la cuenta de prueba de Usuario y revisar la vista permitida que aparece.
        # Entrar button
        elem = page.locator("[data-test=\"login-submit\"]")
        await elem.click(timeout=10000)
        
        # -> Abrir el enlace «Gestión de usuarios» y verificar si la cuenta Usuario es redirigida a su vista permitida.
        # GU Gestión de usuarios link
        elem = page.get_by_role("link", name="Gestión de usuarios")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> La cuenta de Usuario fue redirigida a su vista permitida en /perfil.
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: La URL debe indicar la vista permitida del perfil.
        await expect(page).to_have_url(re.compile("/perfil"), timeout=15000), "La URL debe indicar la vista permitida del perfil."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    
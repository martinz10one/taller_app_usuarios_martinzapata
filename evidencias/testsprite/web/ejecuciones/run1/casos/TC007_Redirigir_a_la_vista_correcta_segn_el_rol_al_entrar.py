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
        
        # -> Abrir la ruta de inicio de sesión y observar si aparece el formulario.
        await page.goto("http://localhost:5173/login")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Iniciar sesión con la cuenta de administrador y comprobar a qué vista privada conduce.
        # tu@email.com email field
        elem = page.locator("[data-test=\"login-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("admin@demo.com")
        
        # -> Iniciar sesión con la cuenta de administrador y comprobar a qué vista privada conduce.
        # password field
        elem = page.locator("[data-test=\"login-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Admin123!")
        
        # -> Iniciar sesión con la cuenta de administrador y comprobar a qué vista privada conduce.
        # Entrar button
        elem = page.locator("[data-test=\"login-submit\"]")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> El administrador llega a la vista privada de gestión de usuarios.
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: La URL confirma que se abrió la vista de gestión de usuarios.
        await expect(page).to_have_url(re.compile("/usuarios"), timeout=15000), "La URL confirma que se abri\u00f3 la vista de gesti\u00f3n de usuarios."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    
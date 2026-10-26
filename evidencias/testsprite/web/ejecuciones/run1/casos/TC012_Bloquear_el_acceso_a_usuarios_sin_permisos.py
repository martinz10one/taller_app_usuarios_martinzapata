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
        
        # -> Abrir la ruta de inicio de sesión especificada y comprobar si aparece el formulario.
        await page.goto("http://localhost:5173/login")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Iniciar sesión con las credenciales visibles de la cuenta Usuario y comprobar el destino al que conduce el inicio de sesión.
        # tu@email.com email field
        elem = page.locator("[data-test=\"login-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("ana@demo.com")
        
        # -> Iniciar sesión con las credenciales visibles de la cuenta Usuario y comprobar el destino al que conduce el inicio de sesión.
        # password field
        elem = page.locator("[data-test=\"login-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Usuario123")
        
        # -> Iniciar sesión con las credenciales visibles de la cuenta Usuario y comprobar el destino al que conduce el inicio de sesión.
        # Entrar button
        elem = page.locator("[data-test=\"login-submit\"]")
        await elem.click(timeout=10000)
        
        # -> Abrir la ruta /usuarios y comprobar a qué página se redirige la cuenta Usuario y si el panel de administración se mantiene oculto.
        await page.goto("http://localhost:5173/usuarios")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # --> Assertions to verify final state
        
        # --> Al intentar abrir /usuarios, la usuaria fue redirigida a /perfil.
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: La usuaria debe ser redirigida a /perfil.
        await expect(page).to_have_url(re.compile("/perfil"), timeout=15000), "La usuaria debe ser redirigida a /perfil."
        
        # --> Se mostró el perfil de usuario en lugar del panel de administración.
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: Debe mostrarse la navegación del perfil de usuario.
        await expect(page.locator("#main-nav").nth(0)).to_contain_text("Mi perfil", timeout=15000), "Debe mostrarse la navegaci\u00f3n del perfil de usuario."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    
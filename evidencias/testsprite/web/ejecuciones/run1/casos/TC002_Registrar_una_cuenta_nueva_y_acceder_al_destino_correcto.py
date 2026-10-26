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
        
        # -> Abrir la ruta de registro indicada y comprobar si se muestra el formulario.
        await page.goto("http://localhost:5173/registro")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Completar y enviar el formulario «Crear cuenta» con datos nuevos válidos, y comprobar la página de destino resultante.
        # text field
        elem = page.locator("[data-test=\"register-name\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Visitante QA")
        
        # -> Completar y enviar el formulario «Crear cuenta» con datos nuevos válidos, y comprobar la página de destino resultante.
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.visitor.20261026@example.com")
        
        # -> Completar y enviar el formulario «Crear cuenta» con datos nuevos válidos, y comprobar la página de destino resultante.
        # password field
        elem = page.locator("[data-test=\"register-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Visitante2026A")
        
        # -> Completar y enviar el formulario «Crear cuenta» con datos nuevos válidos, y comprobar la página de destino resultante.
        # password field
        elem = page.locator("[data-test=\"register-confirmation\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Visitante2026A")
        
        # -> Completar y enviar el formulario «Crear cuenta» con datos nuevos válidos, y comprobar la página de destino resultante.
        # Crear cuenta button
        elem = page.locator("[data-test=\"register-submit\"]")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> La cuenta quedó autenticada y fue dirigida al área de perfil correspondiente al rol Usuario.
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: La cuenta debe dirigirse a su área de perfil.
        await expect(page).to_have_url(re.compile("/perfil"), timeout=15000), "La cuenta debe dirigirse a su \u00e1rea de perfil."
        await page.locator("[data-test=\"logout\"]").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: La opción para cerrar sesión debe estar visible para confirmar que la cuenta está autenticada.
        await expect(page.locator("[data-test=\"logout\"]").nth(0)).to_be_visible(timeout=15000), "La opci\u00f3n para cerrar sesi\u00f3n debe estar visible para confirmar que la cuenta est\u00e1 autenticada."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    
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
        
        # -> Abrir el formulario de registro mediante el enlace «Crea una».
        # Crea una link
        elem = page.locator("[data-test=\"go-register\"]")
        await elem.click(timeout=10000)
        
        # -> Completar el formulario «Crear cuenta» con datos únicos válidos para un visitante.
        # text field
        elem = page.locator("[data-test=\"register-name\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("QA Visitante 20261026")
        
        # -> Completar el formulario «Crear cuenta» con datos únicos válidos para un visitante.
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.visitante.20261026@example.com")
        
        # -> Completar el formulario «Crear cuenta» con datos únicos válidos para un visitante.
        # password field
        elem = page.locator("[data-test=\"register-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("PruebaQa2026!")
        
        # -> Completar el formulario «Crear cuenta» con datos únicos válidos para un visitante.
        # password field
        elem = page.locator("[data-test=\"register-confirmation\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("PruebaQa2026!")
        
        # -> Enviar el formulario «Crear cuenta» y comprobar si el visitante llega autenticado a su vista privada.
        # Crear cuenta button
        elem = page.locator("[data-test=\"register-submit\"]")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> El usuario regular llega a su vista privada «Mi perfil».
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: La URL debe corresponder a la vista privada del perfil.
        await expect(page).to_have_url(re.compile("/perfil"), timeout=15000), "La URL debe corresponder a la vista privada del perfil."
        
        # --> La sesión del usuario está autenticada y ofrece la opción «Cerrar sesión».
        await page.locator("[data-test=\"logout\"]").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: La opción «Cerrar sesión» debe estar visible para una sesión autenticada.
        await expect(page.locator("[data-test=\"logout\"]").nth(0)).to_be_visible(timeout=15000), "La opci\u00f3n \u00abCerrar sesi\u00f3n\u00bb debe estar visible para una sesi\u00f3n autenticada."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    
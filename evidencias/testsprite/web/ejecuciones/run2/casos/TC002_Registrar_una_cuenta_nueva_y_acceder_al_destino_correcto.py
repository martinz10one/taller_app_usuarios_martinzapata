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
        
        # -> Completar los campos visibles del registro con datos de prueba válidos y nuevos.
        # text field
        elem = page.locator("[data-test=\"register-name\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Usuario QA Octubre")
        
        # -> Completar los campos visibles del registro con datos de prueba válidos y nuevos.
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.visitante.20261026@example.com")
        
        # -> Completar los campos visibles del registro con datos de prueba válidos y nuevos.
        # password field
        elem = page.locator("[data-test=\"register-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("TestPass123")
        
        # -> Completar los campos visibles del registro con datos de prueba válidos y nuevos.
        # password field
        elem = page.locator("[data-test=\"register-confirmation\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("TestPass123")
        
        # -> Enviar el formulario con «Crear cuenta» y comprobar el destino mostrado después del registro.
        # Crear cuenta button
        elem = page.locator("[data-test=\"register-submit\"]")
        await elem.click(timeout=10000)
        
        # -> Enter a new unique email address in the registration form and check that the duplicate-email validation clears.
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.visitante.20261026b@example.com")
        
        # -> Reemplazar el correo por una dirección nueva y comprobar si desaparece el aviso de correo ya registrado.
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.visitante.20261026c@example.com")
        
        # -> Reemplazar el correo con otra dirección de prueba y comprobar que desaparezca el aviso de duplicado.
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.visitante.20261026d@example.com")
        
        # -> Reemplazar el correo por una dirección de prueba nueva y verificar si desaparece el aviso de duplicado.
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.visitante.20261026.847291@example.com")
        
        # -> Probar una dirección de correo de dominio diferente y comprobar si la validación de correo duplicado desaparece.
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.visitante.20261026@gmail.com")
        
        # -> Cambiar el email del formulario por una dirección nueva con otro dominio y revisar la validación que muestra la página.
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.visitante.20261026@outlook.com")
        
        # -> Probar una dirección de correo distinta en el campo «Email» y revisar el mensaje de validación mostrado por el formulario.
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.verify.847291@yahoo.com")
        
        # --> Assertions to verify final state
        
        # --> Tras registrarse, el usuario debe salir de /registro hacia un destino permitido.
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: Expected registration to navigate away from /registro to an allowed destination.
        await expect(page).to_have_url(re.compile("^https?://localhost:5173/(?!registro(?:[/?#]|$)).+"), timeout=15000), "Expected registration to navigate away from /registro to an allowed destination."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    
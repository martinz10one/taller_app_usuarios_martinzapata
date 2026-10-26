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
        
        # -> Abrir el formulario de registro desde el enlace «Crea una».
        # Crea una link
        elem = page.locator("[data-test=\"go-register\"]")
        await elem.click(timeout=10000)
        
        # -> Complete the visible registration fields with valid new account details and submit “Crear cuenta.”
        # text field
        elem = page.locator("[data-test=\"register-name\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("QA Test User")
        
        # -> Complete the visible registration fields with valid new account details and submit “Crear cuenta.”
        # tu@email.com email field
        elem = page.locator("[data-test=\"register-email\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.tc002.20261026.153942@example.com")
        
        # -> Complete the visible registration fields with valid new account details and submit “Crear cuenta.”
        # password field
        elem = page.locator("[data-test=\"register-password\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("QaTest2026!")
        
        # -> Complete the visible registration fields with valid new account details and submit “Crear cuenta.”
        # password field
        elem = page.locator("[data-test=\"register-confirmation\"]")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("QaTest2026!")
        
        # -> Complete the visible registration fields with valid new account details and submit “Crear cuenta.”
        # Crear cuenta button
        elem = page.locator("[data-test=\"register-submit\"]")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> The newly registered user is authenticated as Usuario on the role-appropriate profile page.
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: The user should land on the profile page.
        await expect(page).to_have_url(re.compile("/perfil"), timeout=15000), "The user should land on the profile page."
        # Assert-outcome: not verified — the export-time check could not be evaluated
        # Assert: The authenticated navigation should show the Usuario role.
        await expect(page.locator("#main-nav").nth(0)).to_contain_text("Usuario", timeout=15000), "The authenticated navigation should show the Usuario role."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    
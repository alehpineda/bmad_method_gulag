import pytest
from playwright.sync_api import sync_playwright, expect

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        yield page
        browser.close()

def test_e2e_ui_flow(playwright_instance):
    page = playwright_instance
    # Assume API is running on localhost:8000; for test, start server or mock
    # For CI, use pytest fixture to start uvicorn, but simplify: assume running
    page.goto("http://localhost:8000/ui/")
    
    # Input "1" and submit
    page.fill("#search-input", "1")
    page.click("button[type='submit']")
    page.wait_for_selector("#pokemon-card", state="visible")
    
    # Assert card renders
    expect(page.locator("#header")).to_contain_text("#1 Bulbasaur")
    expect(page.locator("#physical")).to_contain_text("Height: 0.7 m")
    expect(page.locator("#physical")).to_contain_text("Weight: 6.9 kg")
    expect(page.locator("#types")).to_contain_text("grass")
    expect(page.locator("#types")).to_contain_text("poison")
    
    # Stats bars (HP 45/255 ~18%)
    hp_bar = page.locator("#stats div:first-child div div")
    expect(hp_bar).to_have_css("width", "17.6%")  # Approx 45/255*100=17.65
    
    # Default sprite
    expect(page.locator("#sprite-img")).to_be_visible()
    
    # Toggle shiny (assume button exists)
    shiny_btn = page.locator("text=front shiny").first
    if shiny_btn.is_visible():
        shiny_btn.click()
        page.wait_for_load_state("networkidle")
        expect(page.locator("#sprite-img")).to_have_attribute("src", expect.string_containing("shiny"))
    
    # Toggle female (should fallback)
    female_btn = page.locator("text=front female").first
    if female_btn.is_visible():
        female_btn.click()
        page.wait_for_load_state("networkidle")
        expect(page.locator("#sprite-fallback")).to_be_visible()
        expect(page.locator("#sprite-fallback")).to_contain_text("Unavailable")
    
    # Invalid ID error
    page.fill("#search-input", "999")
    page.click("button[type='submit']")
    expect(page.locator("#error")).to_be_visible()
    expect(page.locator("#error")).to_contain_text("not found")
    expect(page.locator("#pokemon-card")).to_be_hidden()
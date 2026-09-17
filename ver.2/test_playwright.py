from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME = Path.home() / "browsers/chrome/chrome-linux64/chrome"

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=str(CHROME),
        headless=True
    )

    page = browser.new_page()
    page.goto("https://www.google.com", timeout=60000)

    print("Title:", page.title())
    print("URL:", page.url)

    browser.close()

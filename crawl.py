from pathlib import Path
from playwright.sync_api import sync_playwright

WEB_URL = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
CHROME = Path.home() / "browsers/chrome/chrome-linux64/chrome"

PROJECT_ROOT = Path(__file__).resolve().parent

DOWNLOAD_DIR = PROJECT_ROOT / "Data" / "Temporary Save"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    print("Starting Chrome...")

    browser = p.chromium.launch(
        executable_path=str(CHROME),
        headless=False,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    )

    context = browser.new_context(
        accept_downloads=True
    )

    page = context.new_page()

    print("Opening:", WEB_URL)

    page.goto(
        WEB_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    print("Title:", page.title())
    print("URL:", page.url)

    page.wait_for_selector(
        'table[title="牌告匯率"]',
        timeout=30000,
    )

    print("Exchange rate table loaded")

    csv_link = page.locator(
        'a[href="/xrt/flcsv/0/day"]'
    )

    print("CSV link count:", csv_link.count())

    if csv_link.count() == 0:
        raise RuntimeError("找不到 CSV 下載連結")

    with page.expect_download(timeout=30000) as download_info:
        csv_link.click()

    download = download_info.value

    print("Download URL:", download.url)
    print("Suggested filename:", download.suggested_filename)

    csv_file = DOWNLOAD_DIR / download.suggested_filename
    download.save_as(csv_file)

    print("CSV saved:", csv_file.resolve())

    browser.close()

data = csv_file.read_bytes()

if b"Challenge Validation" in data:
    raise RuntimeError("下載內容是 Challenge HTML，不是 CSV")

print("Done")
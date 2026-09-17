# utils/fx.py
import re
import os
import datetime
import pandas as pd
import datetime as dt

from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .config import (
    CURRENCIES,
    TYPES,
    HISTDL_DIR,
    CHROME_PATH,
    CHROME_ARGS,
)

# 先沿用你原本的函式（避免一次改太多）:contentReference[oaicite:4]{index=4}
# from Download_historical import fetch_twbank_exchange, get_and_save_exchange_rates

_CURRENCY_MAP = {
    "美元": "USD",
    "日圓": "JPY",
    "歐元": "EUR",
    "英鎊": "GBP",
    "港幣": "HKD",
    "澳幣": "AUD",
    "加拿大幣": "CAD",
    "新加坡幣": "SGD",
    "瑞士法郎": "CHF",
    "人民幣": "CNY",
}
def _parse_float(s: str):
    if s is None: return None
    s = s.strip().replace(",", "")
    if s in {"", "-", "—", "–", "N/A", "n/a"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None

def _get_quoted_datetime(soup: BeautifulSoup):
    info_p = soup.select_one("p.text-info")
    if not info_p: return None
    m = re.search(r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2})", info_p.get_text(strip=True))
    return pd.to_datetime(m.group(1)) if m else None

def _fetch_html_with_browser(url: str) -> str:

    if not CHROME_PATH.exists():
        raise RuntimeError(
            f"Chrome executable does not exist: {CHROME_PATH}"
        )

    with sync_playwright() as p:

        browser = p.chromium.launch(
            executable_path=str(CHROME_PATH),
            headless=False,
            args=CHROME_ARGS,
        )

        try:
            context = browser.new_context()
            page = context.new_page()

            print(f"Opening: {url}")

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            # 等臺銀 Challenge
            for i in range(60):

                title = page.title()

                if "Challenge Validation" not in title:
                    break

                print(f"Challenge... {i + 1}")
                page.wait_for_timeout(1000)

            else:
                raise RuntimeError(
                    "Bank of Taiwan Challenge did not complete."
                )

            # 等匯率 table
            page.wait_for_selector(
                "table.table",
                timeout=30000,
            )

            print("Bank of Taiwan page loaded")

            return page.content()

        finally:
            browser.close()

def fetch_twbank_exchange(
    URL,
    save_html: bool = False,
    save_directory=None,
    currencies=None,
) -> pd.DataFrame:

    html = _fetch_html_with_browser(URL)

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    quoted_dt = _get_quoted_datetime(soup)
    if quoted_dt is None: print("Warning: Cannot find Quoted Date. Set Date=None")

    table = soup.select_one("table.table")
    if not table: raise RuntimeError("Cannot find rate table.")

    tbody = table.find("tbody")
    if not tbody: raise RuntimeError("Cannot find tbody in rate table.")
    wanted = set(currencies) if currencies else None

    records = []
    for tr in tbody.select("tr"):
        tds = tr.find_all("td")
        if len(tds) < 5: continue
        currency_text = tds[0].get_text(" ", strip=True)
        m = re.search(r"\(([A-Z]{3})\)", currency_text)
        code = m.group(1) if m else None

        if not code:
            code = next((v for k, v in _CURRENCY_MAP.items() if k in currency_text), None)

        if not code: continue
        if wanted and code not in wanted: continue

        cash_buy  = _parse_float(tds[1].get_text())
        cash_sell = _parse_float(tds[2].get_text())
        spot_buy  = _parse_float(tds[3].get_text())
        spot_sell = _parse_float(tds[4].get_text())

        records.append({"Date": quoted_dt,
                        "Currency": code,
                        "Cash": cash_buy,
                        "Cash.1": cash_sell,
                        "Spot": spot_buy,
                        "Spot.1": spot_sell,
                        })
    output = pd.DataFrame(records, columns=["Date", "Currency", "Cash", "Cash.1", "Spot", "Spot.1"])
    if save_html: output.to_csv(save_directory,index=False, float_format="%.4f")
    return output

def update_file(dataframe:pd.DataFrame,
                update_file:str,
                currencies=None,
                save_snapshot: bool=False) -> pd.DataFrame:
    dataframe = dataframe.set_index("Currency")
    for cur in currencies:
        file = os.path.join(update_file.format(currency=cur))
        if not os.path.exists(file):
            history = pd.DataFrame(columns=['Date','Cash','Spot','Cash.1','Spot.1'])
        else:
            history = pd.read_csv(file)
        tmp = dataframe.loc[[cur], :]
        tmp = tmp.loc[:, history.columns] if not history.empty else tmp
        
        history = pd.concat([history, tmp], ignore_index=True)
        history = history.drop_duplicates(subset=['Date'], keep='last')
        history.to_csv(file, index=False,float_format="%.4f")


def update_daily_rates():
    today_str = dt.datetime.today().strftime("%Y%m%d_%H%M%S")
    df = fetch_twbank_exchange(save_html=True,
                               save_directory=f"exchange_rate_{today_str}.csv",
                               currencies=CURRENCIES)
    update_file(dataframe=df, currencies=CURRENCIES,save_snapshot=False)
    

import re
import os
import requests
import datetime
import pandas as pd
from bs4 import BeautifulSoup

def fetch_twbank_exchange(target_currencies=['USD', 'JPY', 'EUR', 'CNY']):
    url = "https://rate.bot.com.tw/xrt/all/day"
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, "html.parser")

    quoted = None
    info_p = soup.find("p", class_="text-info")
    if info_p and info_p.text:
        m = re.search(r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2})', info_p.text)
        if m:
            quoted = m.group(1)
    if quoted is None:
        print("Warning： Cannot find Quoted Date. Replace with None")

    table = soup.find("table", class_="table")
    rows = table.find("tbody").find_all("tr")
    records = []

    for row in rows:
        cols = row.find_all("td")
        if not cols or len(cols) < 5:
            continue
        currency = cols[0].text.strip()
        for cur in target_currencies:
            if cur in currency:
                try:
                    record = {
                        "Date": pd.to_datetime(quoted),
                        "Currency": cur,
                        "Cash": float(cols[1].text.replace(',', '').strip()) if cols[1].text.strip() else None,
                        "Cash.1": float(cols[2].text.replace(',', '').strip()) if cols[2].text.strip() else None,
                        "Spot": float(cols[3].text.replace(',', '').strip()) if cols[3].text.strip() else None,
                        "Spot.1": float(cols[4].text.replace(',', '').strip()) if cols[4].text.strip() else None,
                    }
                    records.append(record)
                except Exception as e:
                    print(f"Parse error for {cur}: {e}")
                break

    df = pd.DataFrame(records, columns=["Date", "Currency", "Cash", "Cash.1", "Spot", "Spot.1"])
    return df.set_index("Currency")

def get_and_save_exchange_rates():
    currency = ['USD','JPY','EUR','CNY']
    today = datetime.datetime.now()
    today_str = today.strftime("%Y%m%d_%H%M%S")
    date_str = today.strftime("%Y/%m/%d %H:%M:%S")
    data_dir = "../Data/history"
    os.makedirs(data_dir, exist_ok=True)
    save_path = os.path.join(data_dir, f"exchange_rate_{today_str}.csv")

    columns = [
        'Currency',
        'Rate','Cash','Spot',
        'Forward-10Days','Forward-30Days','Forward-60Days','Forward-90Days','Forward-120Days','Forward-150Days','Forward-180Days',
        'Rate.1','Cash.1','Spot.1',
        'Forward-10Days.1','Forward-30Days.1','Forward-60Days.1','Forward-90Days.1','Forward-120Days.1','Forward-150Days.1','Forward-180Days.1'
    ]
    data = pd.read_csv("https://rate.bot.com.tw/xrt/flcsv/0/day", index_col=False, header=0)
    data.columns = columns
    data = data.set_index("Currency")
    data.loc[:,'Rate'  ] = "Buying"
    data.loc[:,'Rate.1'] = "Selling"
    data.to_csv(save_path, index=False)
    
    df_now = data.loc[currency, ['Cash','Spot','Cash.1','Spot.1']].copy()
    df_now['Date'] = date_str
    df_now = df_now[['Date','Cash','Spot','Cash.1','Spot.1']]
    df_now.columns = ['Date','Buy_cash','Buy_spot','Sell_cash','Sell_spot']
    
    for cur in currency:
        file = os.path.join(data_dir, f"{cur}.csv")
        if not os.path.exists(file):
            history = pd.DataFrame(columns=['Date','Buy_cash','Buy_spot','Sell_cash','Sell_spot'])
        else:
            history = pd.read_csv(file)
        tmp = df_now.loc[[cur], :]
        tmp = tmp[history.columns] if not history.empty else tmp
        
        history = pd.concat([history, tmp], ignore_index=True)
        history = history.drop_duplicates(subset=['Date'], keep='last')
        history.to_csv(file, index=False,float_format="%.4f")



if __name__ == "__main__":
    df = fetch_twbank_exchange()
    for t in ['Cash','Spot']:
        for currency in ["USD","JPY","EUR","CNY"]:
            path = f'Historical Download/{currency}_{t}_Historical.csv'
            df_hist = pd.read_csv(path)
            
            df_new = df.loc[[currency]][["Date", f"{t}", f"{t}.1"]].copy()
            df_new.columns = ["Date", "Buying", "Selling"]
            
            existing_dates = set(pd.to_datetime(df_hist["Date"]).dt.strftime('%Y-%m-%d %H:%M'))
            new_date_str = df_new["Date"].iloc[0].strftime('%Y-%m-%d %H:%M')
            if new_date_str not in existing_dates:
                df_all = pd.concat([df_hist, df_new], ignore_index=True)
                df_all["Date"] = pd.to_datetime(df_all["Date"])
                df_all = df_all.sort_values("Date").reset_index(drop=True)
                df_all.to_csv(path, index=False)
                print(f"New data：{currency}_{t} {new_date_str}")
            else:
                print(f"{currency}_{t}: {new_date_str} Existing")

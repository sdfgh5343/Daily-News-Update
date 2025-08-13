# import subprocess
# import sys
# import importlib

# def install(package):
#     subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# with open("requirements.txt", "r") as f:
#     pkgs = [line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')]

# for pkg in pkgs:
#     try:
#         importlib.import_module(pkg)
#     except ImportError:
#         install(pkg)

import os
import glob
import smtplib
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from scipy.interpolate import make_interp_spline
from email import encoders

# 取得腳本所在目錄（不受執行位置影響）
script_dir = os.path.dirname(os.path.abspath(__file__))

# ========= CONFIG =========
visa_url = "https://infovisa.ibz.be/ResultFr.aspx?place=TPE&visumnr=15966"
last_known_status = "En traitement"

sender_email = "sdfgh5343@gmail.com"
receiver_email = "sdfgh5343@gmail.com"
app_password = "axvy lldi amgf bgdx"
# ===========================

def update_currency_history(df):
    for currency in ["USD", "EUR", "CNY"]:
        currency_df = df[df["Currency"] == currency][["Date", "Buy_cash", "Buy_spot", "Sell_cash", "Sell_spot"]]
        today_str = currency_df.iloc[0]["Date"]
        filepath = os.path.join(script_dir, "history", f"{currency}.csv")

        if os.path.exists(filepath):
            old_df = pd.read_csv(filepath)
            if str(today_str) in old_df["Date"].astype(str).values:
                print(f"⚠️ {currency}: 已存在 {today_str} 的資料，略過寫入。")
                continue
            updated_df = pd.concat([old_df, currency_df], ignore_index=True)
            updated_df.to_csv(filepath, index=False)
            print(f"✅ {currency}: 已新增 {today_str} 資料至 history/{currency}.csv")
        else:
            os.makedirs(os.path.join(script_dir, "history"), exist_ok=True)
            currency_df.to_csv(filepath, index=False)
            print(f"✅ {currency}: 建立新檔 history/{currency}.csv 並寫入今日資料")

def update_currency_history2(df):
    for currency in ["USD", "EUR", "CNY"]:
        currency_df = df[df["Currency"] == currency][["Date", "Buy_cash", "Buy_spot", "Sell_cash", "Sell_spot"]].copy()
        
        # 新增：更新日期為現在時間（包含時分秒）
        now_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        currency_df.iloc[0, currency_df.columns.get_loc("Date")] = now_str
        
        # 新增：只保留三位小數
        if currency=="CNY":n=4
        else: n=3
        for col in ["Buy_cash", "Buy_spot", "Sell_cash", "Sell_spot"]:
            currency_df[col] = currency_df[col].round(n)
        
        today_str = now_str
        filepath = os.path.join(script_dir, "history", f"{currency}.csv")

        if os.path.exists(filepath):
            old_df = pd.read_csv(filepath)
            if str(today_str) in old_df["Date"].astype(str).values:
                print(f"⚠️ {currency}: 已存在 {today_str} 的資料，略過寫入。")
                continue
            updated_df = pd.concat([old_df, currency_df], ignore_index=True)
            updated_df.to_csv(filepath, index=False)
            print(f"✅ {currency}: 已新增 {today_str} 資料至 history/{currency}.csv")
        else:
            os.makedirs(os.path.join(script_dir, "history"), exist_ok=True)
            currency_df.to_csv(filepath, index=False)
            print(f"✅ {currency}: 建立新檔 history/{currency}.csv 並寫入今日資料")

def get_current_status():
    response = requests.get(visa_url)
    if response.status_code != 200:
        raise Exception(f"請求失敗: {response.status_code}")
    soup = BeautifulSoup(response.text, 'html.parser')
    decision_cell = soup.find('td', string='Décision: ')
    if decision_cell:
        return decision_cell.find_next('td').get_text(strip=True)
    raise Exception("無法找到簽證狀態")

def get_and_save_exchange_rates():
    url = "https://rate.bot.com.tw/xrt/flcsv/0/day"
    today_str = datetime.today().strftime("%Y%m%d")
    save_path = os.path.join(script_dir, "history", f"exchange_rate_{today_str}.csv")
    os.makedirs(os.path.join(script_dir, "history"), exist_ok=True)

    df = pd.read_csv(url)
    selected_cols = [2, 3, 12, 13]
    df = df.iloc[[0, 14, 18], selected_cols]
    df.columns = ["Buy_cash", "Buy_spot", "Sell_cash", "Sell_spot"]
    df.insert(0, "Currency", ["USD", "EUR", "CNY"])
    df.insert(1, "Date", datetime.today().strftime("%Y/%m/%d"))
    df.to_csv(save_path, index=False)
    return df

def plot_exchange_trend(currency, currency_name, image_filename):
    filepath = os.path.join(script_dir, "history", f"{currency}.csv")
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d", errors='coerce')
    df = df.dropna(subset=["Date"])
    df = df[df["Date"] >= datetime.today() - timedelta(days=30)]

    x = mdates.date2num(df["Date"])
    x_smooth = np.linspace(x.min(), x.max(), 300)

    def smooth_curve(y_values):
        if len(x) < 4:
            return x, y_values
        spline = make_interp_spline(x, y_values, k=3)
        return x_smooth, spline(x_smooth)

    x1, y1 = smooth_curve(df["Buy_cash"].values)
    x2, y2 = smooth_curve(df["Sell_cash"].values)
    x3, y3 = smooth_curve(df["Buy_spot"].values)
    x4, y4 = smooth_curve(df["Sell_spot"].values)

    plt.figure(figsize=(10, 5))
    plt.plot_date(x1, y1, '-', color='red', label="Cash Buy")
    plt.plot_date(x2, y2, '-', color='red', label="Cash Sell")
    plt.plot_date(x3, y3, '--', color='blue', label="Spot Buy")
    plt.plot_date(x4, y4, '--', color='blue', label="Spot Sell")

    # 原始資料點標記
    plt.plot(df["Date"], df["Buy_cash"], 'o', color='red', alpha=0.4)
    plt.plot(df["Date"], df["Sell_cash"], 'o', color='red', alpha=0.4)
    plt.plot(df["Date"], df["Buy_spot"], 'x', color='blue', alpha=0.4)
    plt.plot(df["Date"], df["Sell_spot"], 'x', color='blue', alpha=0.4)

    plt.title(f"{currency_name} Trends (Last 30 Days)")
    plt.xlabel("Date")
    plt.ylabel("Exchange Rate")
    plt.legend(loc='best')
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.tight_layout()
    plt.savefig(os.path.join(script_dir, image_filename))
    plt.close()

def plot_exchange_trend2(image_filename):
    history_dir = os.path.join(script_dir, 'history')

    filepath = []
    currencies = ['USD', 'EUR', 'CNY']
    for currency in currencies:
        pattern = os.path.abspath(os.path.join(history_dir, f"{currency}.csv"))
        matched = glob.glob(pattern)
        filepath.extend(matched)
    # print(filepath)

    fig, ax = plt.subplots(3,1,dpi=300)
    for i, file in enumerate(filepath):
        df = pd.read_csv(file)
        df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d %H:%M:%S", errors='coerce')
        df = df.dropna(subset=["Date"])
        df = df[df["Date"] >= datetime.today() - timedelta(days=30)]

        x = mdates.date2num(df["Date"])
        x_smooth = np.linspace(x.min(), x.max(), 300)

        def smooth_curve(y_values):
            if len(x) < 4:
                return x, y_values
            spline = make_interp_spline(x, y_values, k=3)
            return x_smooth, spline(x_smooth)

        x1, y1 = smooth_curve(df["Buy_cash"].values)
        x2, y2 = smooth_curve(df["Sell_cash"].values)
        x3, y3 = smooth_curve(df["Buy_spot"].values)
        x4, y4 = smooth_curve(df["Sell_spot"].values)

        ax[i].plot(x1, y1, '-', color='red', label="Cash Buy",lw=0.7)
        ax[i].plot(x2, y2, '-', color='red', label="Cash Sell",lw=0.7)
        ax[i].plot(x3, y3, '--', color='blue', label="Spot Buy",lw=0.7)
        ax[i].plot(x4, y4, '--', color='blue', label="Spot Sell",lw=0.7)

        # 原始資料點標記
        ax[i].plot(df["Date"], df["Buy_cash"], 'o', color='red', alpha=0.4, markersize=2)
        ax[i].plot(df["Date"], df["Sell_cash"], 'o', color='red', alpha=0.4, markersize=2)
        ax[i].plot(df["Date"], df["Buy_spot"], 'x', color='blue', alpha=0.4, markersize=2)
        ax[i].plot(df["Date"], df["Sell_spot"], 'x', color='blue', alpha=0.4, markersize=2)

        ax[i].set_title(f"{currencies[i]} Trends (Last 30 Days)",fontsize=10)
        ax[i].set_xlabel("Date",fontsize=5)
        ax[i].set_ylabel("Exchange Rate",fontsize=5)
        ax[i].axes.tick_params(labelsize=5)
        ax[i].legend(loc='best',fontsize=5)
        ax[i].grid(True)
        ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.tight_layout()
    plt.savefig(os.path.join(script_dir, image_filename))
    # plt.show()
    plt.close()

# def generate_email_body(rate_df, visa_status):
def generate_email_body(rate_df, news):
    usd = rate_df[rate_df['Currency'] == 'USD'].iloc[0]
    eur = rate_df[rate_df['Currency'] == 'EUR'].iloc[0]
    cny = rate_df[rate_df['Currency'] == 'CNY'].iloc[0]

    body = f"""
<div style="font-family: 'Microsoft JhengHei', sans-serif; font-size: 15px; line-height: 1.6;">
<h3>📈 Today's Currency</h3>
<b>📌 美金 (USD)</b><br>
現金買入: {usd['Buy_cash']:.4f} ｜ 現金賣出: {usd['Sell_cash']:.4f} ｜ 平均: {(usd['Buy_cash'] + usd['Sell_cash']) / 2:.4f}<br>
即期買入: {usd['Buy_spot']:.4f} ｜ 即期賣出: {usd['Sell_spot']:.4f} ｜ 平均: {(usd['Buy_spot'] + usd['Sell_spot']) / 2:.4f}<br><br>

<b>📌 歐元 (EUR)</b><br>
現金買入: {eur['Buy_cash']:.4f} ｜ 現金賣出: {eur['Sell_cash']:.4f} ｜ 平均: {(eur['Buy_cash'] + eur['Sell_cash']) / 2:.4f}<br>
即期買入: {eur['Buy_spot']:.4f} ｜ 即期賣出: {eur['Sell_spot']:.4f} ｜ 平均: {(eur['Buy_spot'] + eur['Sell_spot']) / 2:.4f}<br><br>

<b>📌 人民幣 (CNY)</b><br>
現金買入: {cny['Buy_cash']:.4f} ｜ 現金賣出: {cny['Sell_cash']:.4f} ｜ 平均: {(cny['Buy_cash'] + cny['Sell_cash']) / 2:.4f}<br>
即期買入: {cny['Buy_spot']:.4f} ｜ 即期賣出: {cny['Sell_spot']:.4f} ｜ 平均: {(cny['Buy_spot'] + cny['Sell_spot']) / 2:.4f}<br>
🔗 <a href="https://rate.bot.com.tw/xrt?Lang=zh-TW" target="_blank">台銀即時匯率查詢</a><br><br>

<h3> CNN Business News </h3>
<pre style="font-family: 'Microsoft JhengHei', monospace; font-size: 13px;">
{news}
</pre>
</div>
"""
    return body

# <h3>🛂 簽證狀態</h3>
# 目前簽證狀態為：<b>{visa_status}</b><br>
# 🔗 <a href="https://infovisa.ibz.be/ResultFr.aspx?place=TPE&visumnr=15966" target="_blank">官方查詢網址</a>

def send_email(subject, body, image_paths=None):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # 加入文字內容（純文字或 HTML）
    msg.attach(MIMEText(body, "html"))  # ← 可改為 "html" 若你仍想支援 HTML 格式

    # 加入圖像附件
    if image_paths:
        for image_path in image_paths:
            full_path = os.path.join(script_dir, image_path)
            with open(full_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(image_path)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)

    # 傳送郵件
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


def get_daily_cnn_business_news(limit=20):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DailyNewsBot/1.0; your.email@example.com)"
    }
    url = "https://edition.cnn.com/business"
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    cards = soup.select("div.container__field-links div.card")
    news_items = []
    
    for card in cards[:limit]:
        # 找到第二個 a href
        a_tags = card.select("a[href]")
        if len(a_tags) >= 2:
            link = "https://edition.cnn.com" + a_tags[1]["href"]
        else:
            continue  # 沒有第二個連結則跳過
        
        # 標題在這個結構下
        title_tag = card.select_one("div.container__headline span.container__headline-text")
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            title = "No title found"

        formatted = f'<b>{title}</b>\n{link}'
        news_items.append(formatted)

    return "\n\n".join(news_items)


def main():
    try:
        # ✅ 假日跳過寄信
        today = datetime.today().weekday()  # 0=Monday, 6=Sunday
        if today >= 5:
            print("📭 週末假日，不寄送匯率與簽證更新郵件。")
            return

        # visa_status = get_current_status()
        news = get_daily_cnn_business_news()
        rate_df = get_and_save_exchange_rates()
        update_currency_history2(rate_df)

        # 產生三張圖
        # plot_exchange_trend("USD", "USD", "usd_trend.png")
        # plot_exchange_trend("EUR", "EUR", "eur_trend.png")
        # plot_exchange_trend("CNY", "CNY", "cny_trend.png")
        plot_exchange_trend2("Currency.png")


        image_paths = ["usd_trend.png", "eur_trend.png", "cny_trend.png"]
        image_paths = ["Currency.png"]
        # email_body = generate_email_body(rate_df, visa_status)
        email_body = generate_email_body(rate_df, news)
        send_email("📬 匯率與美日CNN新聞", email_body, image_paths=image_paths)
        print("✅ Email 已成功寄出。")

    except Exception as e:
        print("❌ 錯誤發生：", e)
        send_email("❌ 系統錯誤通知", f"發生錯誤：\n{str(e)}")


if __name__ == "__main__":
    main()
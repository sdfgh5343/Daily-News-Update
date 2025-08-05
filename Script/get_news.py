# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 12:08:42 2025

@author: u0156396
"""
import requests
from bs4 import BeautifulSoup

def get_daily_cnn_business_news_txt(filename="cnn_news.txt", limit=20):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DailyNewsBot/1.0; your.email@example.com)"
    }
    url = "https://edition.cnn.com/business"
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    cards = soup.select("div.container__field-links div.card")
    news_items = []

    for card in cards[:limit]:
        a_tags = card.select("a[href]")
        if len(a_tags) >= 2:
            link = "https://edition.cnn.com" + a_tags[1]["href"]
        else:
            continue
        title_tag = card.select_one("div.container__headline span.container__headline-text")
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            title = "No title found"
        # 標題和網址 tab 分隔（一行一則）
        news_items.append(f"{title}\t{link}")

    # 儲存為 txt
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(news_items))

    print(f"已儲存 {len(news_items)} 則新聞到 {filename}")

if __name__ == "__main__":
    get_daily_cnn_business_news_txt("../News/cnn_news.txt", limit=20)
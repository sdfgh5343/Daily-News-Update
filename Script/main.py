import datetime
import pandas as pd
from get_news import get_daily_cnn_business_news_txt
from Download_historical import fetch_twbank_exchange, get_and_save_exchange_rates

if __name__ == "__main__":
    # 下載歷史資料
    if datetime.datetime.today().hour >= 12:
        df = fetch_twbank_exchange()
        for t in ['Cash','Spot']:
            for currency in ["USD","JPY","EUR","CNY"]:
                path = f'../Data/Historical Download/{currency}_{t}_Historical.csv'
                df_hist = pd.read_csv(path)
                
                df_new = df.loc[[currency]][["Date", f"{t}", f"{t}.1"]].copy()
                df_new.columns = ["Date", "Buying", "Selling"]
                
                existing_dates = set(pd.to_datetime(df_hist["Date"]).dt.strftime('%Y/%m/%d %H:%M'))
                new_date_str = df_new["Date"].iloc[0].strftime('%Y/%m/%d %H:%M')
                if new_date_str not in existing_dates:
                    df_all = pd.concat([df_hist, df_new], ignore_index=True)
                    df_all["Date"] = pd.to_datetime(df_all["Date"])
                    df_all = df_all.sort_values("Date").reset_index(drop=True)
                    df_all.to_csv(path, index=False)
                    print(f"New data：{currency}_{t} {new_date_str}")
                else:
                    print(f"{currency}_{t}: {new_date_str} Existing")

    # 下載當日資料
    get_and_save_exchange_rates()

    # 下載 CNN Business的新聞
    get_daily_cnn_business_news_txt("../News/cnn_news.txt", limit=20)
    
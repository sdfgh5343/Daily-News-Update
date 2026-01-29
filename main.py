import logging
import datetime as dt
import pandas as pd
# main.py
from pathlib import Path
from utils.fx import  update_daily_rates, fetch_twbank_exchange, update_file
# from utils.news import update_cnn_news
from utils import plot
from utils.config import CURRENCIES

LOG_DIR = Path("log")
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / f"run_{dt.datetime.now():%Y%m%d_%H%M%S}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Program started")

if __name__ == "__main__":
    today = dt.datetime.today()

    ###################################################################
    # Step 1. Download Foreign Exchange Rate                          #
    ###################################################################
    # Historical Foreign Exchange Rate - Closing Rate
    now_utc = dt.datetime.now(dt.timezone.utc)
    if now_utc.hour == 11: # Execute one time everyday
        output1 = fetch_twbank_exchange(URL="https://rate.bot.com.tw/xrt/all/day",
                                        currencies=CURRENCIES)
        # Append data to dataset
        update_file(dataframe = output1,
                    update_file="Data/history/Historical_{currency}.csv",
                    currencies= CURRENCIES)
    
    # Foreign Exchange Rate - Non-Business Hours
    output2 = fetch_twbank_exchange(URL="https://rate.bot.com.tw/xrt?Lang=en-US",
                                    save_html=True,
                                    save_directory=f"Data/Temporary Save/ExchangeRate@{today:%Y%m%d%H%M%S}.csv")
    # Append data to dataset
    update_file(dataframe = output2,
                update_file="Data/Foreign Exchage Rate/Foreign Exchage Rate_{currency}.csv",
                currencies= CURRENCIES)

    
    ###################################################################
    # Step 2. Generate Plotly figure                                  #
    ###################################################################
    for currency in CURRENCIES:
        csv_file = f'Data/history/Historical_{currency}.csv'
        plot.plot_history(csv_file_path=csv_file, 
                          currency=currency,
                          show_html = False,
                          save_html = True,
                          save_directory = f"assets/plot_history_{currency}.html")

        plot.plot_now(csv_file_path =f'Data/Foreign Exchage Rate/Foreign Exchage Rate_{currency}.csv',
                      currency = currency,
                      show_html = False,
                      save_html = True,
                      save_directory = f"assets/plot_now_{currency}.html")
    
    # # 下載 CNN Business的新聞
    # get_daily_cnn_business_news_txt("../News/cnn_news.txt", limit=20)

    
# utils/config.py
from pathlib import Path

CURRENCIES = ["USD", "JPY", "EUR", "CNY"]
TYPES = ["Cash", "Spot"]

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR    = ROOT / "Data"
HISTORY_DIR = DATA_DIR / "history"
HISTDL_DIR  = DATA_DIR / "Historical Download"

NEWS_DIR    = ROOT / "News"
FIG_DIR     = ROOT / "Figure"

CNN_TXT     = NEWS_DIR / "cnn_news.txt"
INDEX_HTML  = ROOT / "index.html"
ASSETS_DIR  = ROOT / "assets"

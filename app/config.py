# app/config.py
"""
Configuration file for the lottery scraper pipeline.
All constants and settings are stored here.
"""

# --- Target ---
TARGET_URL = "https://www.nlb.lk/results/mahajana-sampatha"

# --- Database ---
# This will create a file named 'lottery.db' in the main 'lottery_pipeline' folder
DATABASE_URI = "sqlite:///lottery.db"
TABLE_NAME = "mahajana_sampatha"

# --- Scraper Settings ---
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive'
}

# --- HTML Selectors ---
# The classes of the main <table> containing all results.
RESULTS_TABLE_CLASSES = "w0 tbl"
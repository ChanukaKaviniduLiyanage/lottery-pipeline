# app/scraper.py
"""
Handles all web scraping and HTML parsing logic using Selenium
to render JavaScript-driven content.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
import time

def get_webdriver():
    """Initializes and returns a Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    # ADD THIS LINE:
    options.add_argument("--no-sandbox") # Required for running as 'root' on Linux
    
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize Selenium WebDriver: {e}")
        return None

def fetch_page_content(driver, url, table_classes):
    """
    Fetches the HTML content *after* JavaScript has rendered,
    by waiting for the results table to appear.
    """
    logging.info(f"Fetching data from {url} using Selenium...")
    try:
        driver.get(url)
        
        # --- This is the crucial part ---
        # We wait a max of 10 seconds for the element with
        # class 'w0 tbl' to appear on the page.
        wait = WebDriverWait(driver, 10)
        
        # Convert 'w0 tbl' to a CSS selector '.w0.tbl'
        css_selector = "." + ".".join(table_classes.split())
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        
        logging.info("JavaScript content (results table) has loaded.")
        
        # Give it a tiny extra moment to be safe
        time.sleep(1) 
        
        # Now, get the page source *after* the wait
        return driver.page_source

    except TimeoutException:
        logging.error(f"Timed out waiting for results table ('{table_classes}') to load.")
        return None
    except Exception as e:
        logging.error(f"Error fetching URL {url} with Selenium: {e}")
        return None

# ---
# NOTE: THIS PARSE FUNCTION IS 100% IDENTICAL TO THE ONE
# FROM OUR LAST ATTEMPT. IT SHOULD WORK NOW.
# ---
def parse_results(html_content, table_classes):
    """Parses the HTML to extract lottery results from a table."""
    if html_content is None:
        return pd.DataFrame() # Return empty DataFrame if fetch failed

    logging.info("Parsing HTML content...")
    soup = BeautifulSoup(html_content, 'lxml')
    
    results_table = soup.find('table', class_=table_classes)
    
    if not results_table:
        logging.warning(f"Could not find results table with classes '{table_classes}'.")
        return pd.DataFrame()

    table_body = results_table.find('tbody')
    if not table_body:
        logging.warning("Found table, but no 'tbody' inside it.")
        return pd.DataFrame()

    draw_rows = table_body.find_all('tr')
    
    if not draw_rows:
        logging.warning("Found table body, but no 'tr' rows inside it.")
        return pd.DataFrame()

    logging.info(f"Found {len(draw_rows)} draw rows to parse.")
    
    all_results = []
    for row in draw_rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            logging.warning("Found a table row, but it has less than 2 cells. Skipping.")
            continue

        try:
            cell_draw_date = cells[0]
            draw_number = int(cell_draw_date.find('b').text)
            date_str = cell_draw_date.find('br').next_sibling.strip()
            
            cell_results = cells[1]
            result_items = [li.text for li in cell_results.find_all('li')]
            
            if not result_items:
                 logging.warning(f"Found row {draw_number} but no result items (li). Skipping.")
                 continue

            letter = result_items[0]
            # Use list slicing to avoid errors if there are fewer than 6 numbers
            numbers = [int(n) for n in result_items[1:7]] 

            # Create a full row, filling with None if numbers are missing
            clean_row = {
                'draw_number': draw_number,
                'draw_date': pd.to_datetime(date_str).strftime('%Y-%m-%d'),
                'letter': letter,
                'num1': numbers[0] if len(numbers) > 0 else None,
                'num2': numbers[1] if len(numbers) > 1 else None,
                'num3': numbers[2] if len(numbers) > 2 else None,
                'num4': numbers[3] if len(numbers) > 3 else None,
                'num5': numbers[4] if len(numbers) > 4 else None,
                'num6': numbers[5] if len(numbers) > 5 else None,
            }
            all_results.append(clean_row)

        except Exception as e:
            logging.warning(f"Failed to parse row. Error: {e}. Skipping row.")
    
    return pd.DataFrame(all_results)
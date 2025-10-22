# app/main.py
"""
Main entry point for the ETL pipeline.
This script coordinates the E-T-L process.
"""
import logging
from app import config, database, scraper

# --- Best Practice: Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"), # Saves to pipeline.log
        logging.StreamHandler()            # Prints to console
    ]
)

def run_pipeline():
    """Main function to run the ETL pipeline."""
    
    logging.info("Pipeline started. Initializing WebDriver...")
    driver = scraper.get_webdriver()
    if not driver:
        logging.error("Pipeline stopped: Could not initialize Selenium WebDriver.")
        return

    try:
        # --- 1. EXTRACT ---
        html = scraper.fetch_page_content(
            driver, 
            config.TARGET_URL, 
            config.RESULTS_TABLE_CLASSES
        )
        
        if not html:
            logging.error("Pipeline stopped: Failed to fetch data.")
            return

        # --- 2. TRANSFORM ---
        scraped_df = scraper.parse_results(
            html, 
            config.RESULTS_TABLE_CLASSES
        )
        
        del html 
        logging.info("Optimized: Freed memory by deleting raw HTML content.")

        if scraped_df.empty:
            logging.error("Pipeline stopped: No data was parsed from the page.")
            return

        logging.info(f"Successfully scraped {len(scraped_df)} total results from the page.")

        # --- 3. LOAD ---
        engine = database.get_db_engine(config.DATABASE_URI)
        if not engine:
            logging.error("Pipeline stopped: Could not connect to database.")
            return
        
        existing_draws = database.get_existing_draws(engine, config.TABLE_NAME)
        logging.info(f"Found {len(existing_draws)} draws already in the database.")

        new_results_df = scraped_df[~scraped_df['draw_number'].isin(existing_draws)]
        
        if new_results_df.empty:
            logging.info("No new results to add. Database is already up-to-date.")
        else:
            logging.info(f"Found {len(new_results_df)} new results to save.")
            try:
                saved_count = database.save_new_results(new_results_df, engine, config.TABLE_NAME)
                logging.info(f"Successfully saved {saved_count} new records to the database.")
            except Exception as e:
                logging.error(f"Failed to save new results to database. Error: {e}")

    finally:
        # --- Best Practice: Always close the browser ---
        if driver:
            driver.quit()
        logging.info("Pipeline run finished. WebDriver closed.")

# ---
# This makes the script runnable directly
# ---
if __name__ == "__main__":
    run_pipeline()
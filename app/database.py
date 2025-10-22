# app/database.py
"""
Handles all database connections and transactions.
"""
import pandas as pd
from sqlalchemy import create_engine
import logging

def get_db_engine(uri):
    """Creates and returns a SQLAlchemy engine."""
    try:
        return create_engine(uri)
    except Exception as e:
        logging.error(f"Failed to create database engine: {e}")
        return None

def get_existing_draws(engine, table_name):
    """Fetches the set of all draw numbers already in the database."""
    try:
        # Best Practice: Read *only* the 'draw_number' column for maximum efficiency.
        existing_df = pd.read_sql_table(table_name, con=engine, columns=['draw_number'])
        return set(existing_df['draw_number'])
    except ValueError:
        # This will run if the table doesn't exist yet (e.g., first run)
        logging.info("Table not found. Assuming this is the first run.")
        return set()

def save_new_results(df, engine, table_name):
    """
    Appends a DataFrame of new results to the database.
    Returns the number of rows saved.
    """
    if not df.empty:
        try:
            df.to_sql(
                table_name,
                con=engine,
                if_exists='append',
                index=False
            )
            return len(df)
        except Exception as e:
            logging.error(f"Failed to save data to database: {e}")
            return 0
    return 0
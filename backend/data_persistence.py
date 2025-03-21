import sqlite3
import pandas as pd
import os
import numpy as np

from backend import queries
from utils.logger import logger
import backend.database as db 

DATABASE_PATH = db.DATABASE_PATH

def initialize_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    #Initialize the SQLite database and create table if they don't exist.
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        create_tables(queries.CREATE_TRANSACTIONS)
        create_tables(queries.CREATE_ASSET_PRICE)
        create_tables(queries.CREATE_ASSETS)
        create_tables(queries.CREATE_PORTFOLIOS)
        logger.info("Created schema.")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    finally:
        conn.close()

def create_tables(table):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(table)
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    finally:
        conn.close()

def print_table(table_name="Asset_Transaction"):
    try: 
        conn = sqlite3.connect(DATABASE_PATH)
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        print(f"-----------{table_name}---------------------")
        print(df)
        print("--------------------------------")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        conn.close()

def get_table_schema(table_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    conn.close()
    return [(col[1], col[2]) for col in columns] 

def save_to_db(df, portfolio):
    df['Portfolio'] = portfolio

    try:
        db.save_transactions(df)
        db.save_assets()
        db.save_portfolios()
    except Exception as e:
        logger.error(f"Failed to save_to_db: {e}")
    finally:
        pass





import sqlite3
import pandas as pd
import os
import numpy as np

from backend import queries
from utils.logger import logger

DATABASE_PATH = "db/database.db"

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

   # except Exception as e:
   #     logger.error(f"Failed to initialize database: {e}")
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

def print_table(table_name="transaction"):
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

def save_to_db(df, asset_prices,portfolio):

    df['Portfolio'] = portfolio

    save_transactions(df)
    save_asset_prices(asset_prices)
    save_assets()
    save_portfolios()

def save_asset_prices(asset_prices):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()  
        cursor.execute(queries.DELETE_ASSET_PRICE)
        for asset,current_price in asset_prices.items():
            cursor.execute(queries.INSERT_ASSET_PRICE, (asset,current_price))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to save data to database: {e}")
    finally:
        conn.close()

def save_transactions(df):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()        
        df.to_sql("asset_transaction", conn, if_exists="append",index=False)
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to save data to database: {e}")
    finally:
        conn.close()

def save_assets():
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()        

        cursor.execute(queries.CALCULATE_ASSET_METRICS)
        metrics = cursor.fetchall()
        
        # Update or Insert logic
        for metric in metrics:
            asset, current_price, amount, balance, total_invested, avg_buy_price, realised_profit, unrealised_profit, total_profit = metric
            
            # Check if the asset already exists in asset_metrics
            cursor.execute(queries.COUNT_ASSETS, (asset,))
            exists = cursor.fetchone()[0]
            
            if exists:
                # Update the existing row
                cursor.execute(queries.UPDATE_ASSETS, 
                               (amount, current_price, balance, total_invested, avg_buy_price, realised_profit, unrealised_profit, total_profit, asset))
            else:
                # Insert a new row
                cursor.execute(queries.INSERT_ASSETS,(asset,current_price,amount,balance,total_invested,avg_buy_price,realised_profit,unrealised_profit,total_profit))
        conn.commit()
    except Exception as e:
         logger.error(f"Failed to save data to database: {e}")
    finally:
        conn.close()

def save_portfolios():

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()        
        cursor.execute(queries.SAVE_PORTFOLIO_METRICS)
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to save data to database: {e}")
    finally:
        conn.close()
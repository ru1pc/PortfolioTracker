import sqlite3
from utils.logger import logger
import pandas as pd

import backend.queries as query
import backend.data_persistence as dper


DATABASE_PATH = dper.DATABASE_PATH

def get_all_transactions():
    try:
        conn = sqlite3.connect(DATABASE_PATH)     
        all_transactions=  pd.read_sql_query(query.GET_ALL_TRANSACTIONS,conn)
        logger.info(f"📂 get_all_transactions()")
        return all_transactions
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
    finally:
        conn.close()

def get_assets():
    try:
        conn = sqlite3.connect(DATABASE_PATH)      
        all_assets= pd.read_sql_query(query.GET_ASSETS,conn)
        logger.info(f"📂 get_assets() ")
        return all_assets
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
    finally:
        conn.close()

def get_portfolio_latest_data():
    try:
        conn = sqlite3.connect(DATABASE_PATH)       
        portfolios_data = pd.read_sql_query(query.GET_PORTFOLIO_LATEST_DATA,conn)
        logger.info(f"📂 get_portfolio_latest_data() ")
        return portfolios_data
    except Exception as e:
        logger.error(f"Failed to save data to database: {e}")
    finally:
        conn.close()

def get_transactions_by_portfolio(portfolio_name="default"):
    try:
        conn = sqlite3.connect(DATABASE_PATH)  
        portfolio_transactions = pd.read_sql_query(query.GET_TRANSACTIONS_BY_PORTFOLIO,conn,params=(portfolio_name,))
        logger.info(f"📂 get_transactions_by_portfolio() ")
        return portfolio_transactions
    except Exception as e:
        logger.error(f"Failed to save data to database: {e}")
    finally:
        conn.close()

## ASSET METRICS

def calculate_avg_price_by_asset(asset_name,portfolio="default"):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(query.CALCULATE_AVG_PRICE_BY_ASSET, (portfolio,asset_name))
        avg_price = cursor.fetchone()[0] or 0.0
        logger.info(f"📊 Calculated average price for {asset_name}: ${avg_price:.2f}")
        return avg_price
    except Exception as e:
        logger.error(f"❌ Failed to calculate average price: {e}")
        return 0.0
    finally:
        conn.close()

def calculate_total_invested_by_asset(asset_name):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(query.CALCULATE_TOTAL_COST, (asset_name,))
        total_invested = cursor.fetchone()[0] or 0.0
        logger.info(f"📊 Calculated total invested for {asset_name}: ${total_invested:.2f}")
        return total_invested
    except Exception as e:
        logger.error(f"❌ Failed to calculate total invested: {e}")
        return 0.0
    finally:
        conn.close()


'''
def calculate_realised_profit(asset_name):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        query = """
            SELECT SUM((Price - AvgBuyPrice) * Amount)
            FROM transactions
            WHERE Asset = ? AND Type = 'SELL'
        """
        cursor.execute(query, (asset_name,))
        realised_profit = cursor.fetchone()[0] or 0.0
        logger.info(f"📊 Calculated realised profit for {asset_name}: ${realised_profit:.2f}")
        return realised_profit
    except Exception as e:
        logger.error(f"❌ Failed to calculate realised profit: {e}")
        return 0.0
    finally:
        conn.close()


def get_total_cost_by_year(year): 
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        query = "SELECT SUM(Cost) FROM transactions WHERE Year = ?"
        cursor.execute(query, (year,))
        total_cost = cursor.fetchone()[0] or 0.0
        logger.info(f"📊 Calculated total cost for year: {year}")
        return total_cost
    except Exception as e:
        logger.error(f"❌ Failed to calculate total cost: {e}")
        return 0.0
    finally:
        conn.close()

# Calculate the total profit for a specific asset (realised + unrealised).
def calculate_total_profit(asset_name, current_price):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Realised profit (sum of profits from sell transactions)
        query_realised = """
            SELECT SUM((Price - AvgBuyPrice) * Amount)
            FROM transactions
            WHERE Asset = ? AND Type = 'SELL'
        """
        cursor.execute(query_realised, (asset_name,))
        realised_profit = cursor.fetchone()[0] or 0.0

        # Unrealised profit (current value - total invested)
        query_unrealised = """
            SELECT SUM(Amount), AVG(Price)
            FROM transactions
            WHERE Asset = ? AND Type = 'BUY'
        """
        cursor.execute(query_unrealised, (asset_name,))
        result = cursor.fetchone()
        total_amount = result[0] or 0.0
        avg_buy_price = result[1] or 0.0

        unrealised_profit = (current_price - avg_buy_price) * total_amount

        total_profit = realised_profit + unrealised_profit
        logger.info(f"📊 Calculated total profit for {asset_name}: ${total_profit:.2f}")

        return total_profit
    
    except Exception as e:
        logger.error(f"❌ Failed to calculate total profit: {e}")
        return 0.0
    finally:
        conn.close()




def calculate_unrealised_profit(asset_name, current_price):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        query = """
            SELECT SUM(Amount), AVG(Price)
            FROM transactions
            WHERE Asset = ? AND Type = 'BUY'
        """
        cursor.execute(query, (asset_name,))
        result = cursor.fetchone()
        total_amount = result[0] or 0.0
        avg_buy_price = result[1] or 0.0

        unrealised_profit = (current_price - avg_buy_price) * total_amount
        logger.info(f"📊 Calculated unrealised profit for {asset_name}: ${unrealised_profit:.2f}")
        return unrealised_profit
    except Exception as e:
        logger.error(f"❌ Failed to calculate unrealised profit: {e}")
        return 0.0
    finally:
        conn.close()

# MAL CALCULADO. AS COMPRAS NAO SAO TODAS DOS MESMOS VALORES
def calculate_average_buy_price(asset_name):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        query = """
            SELECT AVG(Price)
            FROM transactions
            WHERE Asset = ? AND Type = 'BUY'
        """
        cursor.execute(query, (asset_name,))
        avg_buy_price = cursor.fetchone()[0] or 0.0
        logger.info(f"📊 Calculated average buy price for {asset_name}: ${avg_buy_price:.2f}")
        return avg_buy_price
    except Exception as e:
        logger.error(f"❌ Failed to calculate average buy price: {e}")
        return 0.0
    finally:
        conn.close()

def calculate_balance(asset_name, current_price):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        query = """
            SELECT SUM(Amount)
            FROM transactions
            WHERE Asset = ?
        """
        cursor.execute(query, (asset_name,))
        total_amount = cursor.fetchone()[0] or 0.0

        balance = total_amount * current_price
        logger.info(f"📊 Calculated balance for {asset_name}: ${balance:.2f}")
        return balance
    except Exception as e:
        logger.error(f"❌ Failed to calculate balance: {e}")
        return 0.0
    finally:
        conn.close()'
'''
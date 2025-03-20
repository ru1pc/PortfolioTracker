import sqlite3
from utils.logger import logger
import pandas as pd

import backend.queries as query
import backend.data_persistence as dper


DATABASE_PATH = dper.DATABASE_PATH

def get_allocation_by(allocation_view="asset"):
    try:
        conn = sqlite3.connect(DATABASE_PATH)     
        if allocation_view == "asset":
            q = query.GET_ALLOCATION_BY_ASSET
            allocation_data=  pd.read_sql_query(q,conn)
        elif allocation_view == "portfolio":
            q = query.GET_ALLOCATION_BY_PORTFOLIO
            allocation_data=  pd.read_sql_query(q,conn)
        else:
            q = query.GET_ALLOCATION.format(filter=allocation_view)
            allocation_data= pd.read_sql_query(q,conn)
        logger.info(f"📂 get_history_overview()")
        return allocation_data
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
    finally:
        conn.close()

def get_portfolio_history(portfolio_name):
    try:
        conn = sqlite3.connect(DATABASE_PATH)     
        overview_history=  pd.read_sql_query(query.GET_HISTORY_BY_PORTFOLIO,conn,params=(portfolio_name,))
        logger.info(f"📂 get_history_overview()")
        return overview_history
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
    finally:
        conn.close()

def get_history_overview():
    try:
        conn = sqlite3.connect(DATABASE_PATH)     
        overview_history=  pd.read_sql_query(query.GET_HISTORY_OVERVIEW,conn)
        logger.info(f"📂 get_history_overview()")
        return overview_history
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
    finally:
        conn.close()

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

def get_holdings(portfolio):
    try:
        conn = sqlite3.connect(DATABASE_PATH)      
        holdings= pd.read_sql_query(query.GET_HOLDINGS_DATA,conn,params=(portfolio,))
        logger.info(f"📂 get_holdings() ")
        return holdings
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
    finally:
        conn.close()
    return
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
'''
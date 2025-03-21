import sqlite3
from utils.logger import logger
import pandas as pd

import backend.queries as query

DATABASE_PATH = "db/database.db"

def get_portfolio_snapshot():
    return

def get_assets_by(allocation_view="Type"):
    try:
        conn = sqlite3.connect(DATABASE_PATH)     
        q = query.GET_ASSETS_BY.format(filter=allocation_view)
        assets_by= pd.read_sql_query(q,conn)
        logger.info(f"📂 get_assets_by()")
        return assets_by
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
    finally:
        conn.close()

def get_portfolio_history(portfolio_name):
    try:
        conn = sqlite3.connect(DATABASE_PATH)     
        portfolio_history=pd.read_sql_query(query.GET_PORTFOLIO_HISTORY,conn,params=(portfolio_name,))
        logger.info(f"📂 get_portfolio_history()")
        return portfolio_history
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
    finally:
        conn.close()

def get_portfolios():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        portfolios = pd.read_sql_query(query.GET_PORTFOLIOS_LIST, conn)
        logger.info(f"📂 get_portfolios()")
        return portfolios
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
    finally:
        conn.close()

def add_new_portfolio(portfolio_name):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(query.ADD_NEW_PORTFOLIO, (portfolio_name,))
        conn.commit()   
    except Exception as e:
        logger.error(f"Failed to add new portfolio: {e}")
    finally:
        conn.close()

def save_asset_prices(asset_prices):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()  
        cursor.execute(query.DELETE_ASSET_PRICE)
        for asset,current_price in asset_prices.items():
            cursor.execute(query.CREATE_ASSET_PRICE, {"Current_Price":current_price,"Asset":asset})
        logger.info(f"🔁 Updated asset price for {asset}")    
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to save asset prices: {e}")
    finally:
        conn.close()

def get_portfolio_history_overview():
    try:
        conn = sqlite3.connect(DATABASE_PATH)     
        overview_history=  pd.read_sql_query(query.GET_PORTFOLIO_HISTORY_OVERVIEW,conn)
        logger.info(f"📂 get_portfolio_history_overview()")
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

def get_all_assets():
    try:
        conn = sqlite3.connect(DATABASE_PATH)      
        all_assets= pd.read_sql_query(query.GET_ALL_ASSETS,conn)
        logger.info(f"📂 get_assets() ")
        return all_assets
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
    finally:
        conn.close()

def get_assets_by_portfolio(portfolio_name):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        assets = pd.read_sql_query(query.GET_ASSETS_BY_PORTFOLIO, conn, params=(portfolio_name,))
        logger.info(f"📂 get_assets_by_portfolio() for {portfolio_name}")
        return assets
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
        logger.error(f"Failed to get_portfolio_latest_data: {e}")
    finally:
        conn.close()

def get_transactions_by_portfolio(portfolio_name="default"):
    try:
        conn = sqlite3.connect(DATABASE_PATH)  
        portfolio_transactions = pd.read_sql_query(query.GET_TRANSACTIONS_BY_PORTFOLIO,conn,params=(portfolio_name,))
        logger.info(f"📂 get_transactions_by_portfolio() ")
        return portfolio_transactions
    except Exception as e:
        logger.error(f"Failed to get_transactions_by_portfolio: {e}")
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

def save_asset_prices(asset_prices):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()  
        cursor.execute(query.DELETE_ASSET_PRICE)
        for asset,current_price in asset_prices.items():
            cursor.execute(query.INSERT_ASSET_PRICE, (asset,current_price))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed save_asset_prices: {e}")
    finally:
        conn.close()

def save_transactions(df):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        for _, row in df.iterrows():
            cursor.execute(query.ADD_NEW_TRANSACTION,row.to_dict())

        conn.commit()
        logger.info(f"✅ Successfully saved {len(df)} transactions to database")
    except Exception as e:
        logger.error(f"Failed to save transactions to database: {e}")
    finally:
        conn.close()

def save_assets():
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()        

        cursor.execute(query.CALCULATE_HOLDINGS_TABLE)
        metrics = cursor.fetchall()
        
        # Update or Insert logic
        for metric in metrics:
            Asset,Amount,Total_Invested,Current_Price,Balance,Average_Buy_Price,Realised_Profit,Unrealised_Profit,Total_Profit = metric
            
            cursor.execute(query.COUNT_ASSETS, (Asset,))
            exists = cursor.fetchone()[0]
            
            if exists:

                cursor.execute(query.UPDATE_ASSETS, 
                               (Asset,Amount,Total_Invested,Current_Price,Balance,Average_Buy_Price,Realised_Profit,Unrealised_Profit,Total_Profit))
            else:
                cursor.execute(query.INSERT_ASSETS,(Asset,Amount,Total_Invested,Current_Price,Balance,Average_Buy_Price,Realised_Profit,Unrealised_Profit,Total_Profit))
        conn.commit()
    except Exception as e:
         logger.error(f"Failed save_assets: {e}")
    finally:
        conn.close()

def save_portfolios():

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()        
        cursor.execute(query.SAVE_PORTFOLIO_METRICS)
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to save_portfolios: {e}")
    finally:
        conn.close()
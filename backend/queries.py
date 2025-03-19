CREATE_TRANSACTIONS="""
CREATE TABLE IF NOT EXISTS asset_transaction  (
    Date DATE,
    Time_UTC_ TEXT,
    Asset TEXT,
    Action TEXT,
    Price REAL,
    Amount REAL,
    Cost REAL,
    Fee REAL,
    Fee_Cost REAL,
    Fee_Coin TEXT,
    Currency TEXT,
    Type TEXT,
    Platform TEXT,
    Portfolio TEXT
);
"""

CREATE_ASSETS="""
CREATE TABLE IF NOT EXISTS asset (
    Asset TEXT,
    Amount REAL,
    Balance REAL,
    Total_Invested REAL,
    Average_Buy_Price REAL, 
    Total_Profit REAL,
    Realised_Profit REAL,
    Unrealised_Profit REAL
);
"""

CREATE_PORTFOLIOS="""
CREATE TABLE IF NOT EXISTS portfolio (
    portfolio TEXT NOT NULL,
    total_invested REAL NOT NULL,
    realised_profit REAL NOT NULL,
    unrealised_profit REAL NOT NULL,
    balance REAL NOT NULL,
    date DATE NOT NULL,
    PRIMARY KEY (portfolio, date)
);
"""

CREATE_ASSET_PRICE="""
CREATE TABLE IF NOT EXISTS current_prices  (
    asset TEXT PRIMARY KEY,
    current_price REAL NOT NULL
);
"""

DELETE_ASSET_PRICE="""
    DELETE FROM current_prices;
"""

GET_PORTFOLIO_LATEST_DATA = """
    SELECT p.*
    FROM portfolio p
    JOIN (
        SELECT portfolio, MAX(date) AS max_date
        FROM portfolio
        GROUP BY portfolio
    ) latest ON p.portfolio = latest.portfolio AND p.date = latest.max_date;
"""

GET_PORTFOLIOS = "SELECT DISTINCT portfolio FROM portfolio"

GET_ALL_TRANSACTIONS = "SELECT * FROM asset_transaction"

GET_ASSETS = "SELECT * FROM asset"

GET_TRANSACTIONS_BY_PORTFOLIO = """
    SELECT * 
    FROM asset_transaction
    WHERE Portfolio = ?
"""

COUNT_ASSETS ="""
SELECT COUNT(*) FROM asset WHERE Asset = :Asset
"""

COUNT_ASSET_PRICE ="""
    SELECT COUNT(*) FROM current_prices WHERE Asset = :Asset
"""

INSERT_ASSET_PRICE ="""
    INSERT INTO current_prices (Asset,current_price)
    VALUES (:asset, :current_price)
"""

UPDATE_ASSETS ="""
    UPDATE asset
    SET Amount = :amount, Balance = :balance, Total_Invested = :total_invested, Average_Buy_Price = :avg_buy_price,
        Realised_Profit = :realised_profit, Unrealised_Profit = :unrealised_profit, Total_Profit = :total_profit
    WHERE Asset = :asset
"""

INSERT_ASSETS ="""
    INSERT INTO asset (Asset, Amount, Balance, Total_Invested, Average_Buy_Price,
        Realised_Profit, Unrealised_Profit, Total_Profit)
    VALUES (:asset, :amount, :balance, :total_invested, :avg_buy_price, :realised_profit, :unrealised_profit, :total_profit)
"""

CALCULATE_ASSET_METRICS = """
WITH asset_summary AS (
    SELECT
        Asset,
        SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE -Amount END) AS amount,
        SUM(CASE WHEN Action = 'SELL' THEN Amount * Price - Fee_Cost ELSE 0 END) AS realised_profit,
        SUM(CASE WHEN Action = 'BUY' THEN Cost ELSE -(Amount * Price - Fee_Cost) END) AS total_invested
    FROM asset_transaction
    GROUP BY Asset
),
average_buy_price AS (
    SELECT
        Asset,
        CASE 
            WHEN SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE 0 END) > 0
            THEN SUM(CASE WHEN Action = 'BUY' THEN Amount * Price ELSE 0 END) / SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE 0 END)
            ELSE 0
        END AS average_buy_price
    FROM asset_transaction
    GROUP BY Asset
),
current_prices AS (
    SELECT 'ADA' AS Asset, 0.70 AS current_price UNION ALL
    SELECT 'ETH' AS Asset, 1914 AS current_price UNION ALL
    SELECT 'XRP' AS Asset, 2.30 AS current_price
),
final_metrics AS (
    SELECT
        s.Asset,
        s.amount,
        s.amount * c.current_price AS balance,
        s.total_invested,
        a.average_buy_price,
        s.realised_profit,
        (s.amount * c.current_price) - (s.total_invested) AS unrealised_profit,
        ((s.amount * c.current_price) - (s.total_invested)) + s.realised_profit AS total_profit
    FROM asset_summary s
    JOIN average_buy_price a ON s.Asset = a.Asset
    JOIN current_prices c ON s.Asset = c.Asset
)
SELECT * FROM final_metrics;
"""

SAVE_PORTFOLIO_METRICS = """
WITH asset_summary AS (
    SELECT
        portfolio,
        asset,
        SUM(CASE WHEN action = 'BUY' THEN amount ELSE -amount END) AS amount_holdings,
        SUM(CASE WHEN action = 'BUY' THEN cost ELSE 0 END) AS total_buy_cost,
        SUM(CASE WHEN action = 'SELL' THEN amount * price - fee_cost ELSE 0 END) AS realised_profit
    FROM asset_transaction
    GROUP BY portfolio, asset
),
current_values AS (
    SELECT
        a.portfolio,
        a.asset,
        a.amount_holdings,
        a.total_buy_cost,
        a.realised_profit,
        c.current_price,
        a.amount_holdings * c.current_price AS balance
    FROM asset_summary a
    JOIN current_prices c ON a.asset = c.asset
),
final_metrics AS (
    SELECT
        portfolio,
        SUM(total_buy_cost - realised_profit) AS total_invested,
        SUM(realised_profit) AS realised_profit,
        SUM(balance - (total_buy_cost - realised_profit)) AS unrealised_profit,
        SUM(balance) AS balance
    FROM current_values
    GROUP BY portfolio
)
INSERT OR REPLACE INTO portfolio (portfolio, total_invested, realised_profit, unrealised_profit, balance, date)
SELECT 
    portfolio, 
    total_invested, 
    realised_profit, 
    unrealised_profit, 
    balance, 
    DATE('now')
FROM final_metrics;
"""
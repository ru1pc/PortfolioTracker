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
    Current_Price REAL,
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

GET_ALLOCATION_BY_ASSET="""
WITH asset_summary AS (
    SELECT
        asset,
        SUM(CASE WHEN action = 'BUY' THEN amount ELSE -amount END) AS amount_holdings
    FROM asset_transaction
    GROUP BY asset
),
current_values AS (
    SELECT
        a.asset,
        a.amount_holdings,
        c.current_price,
        a.amount_holdings * c.current_price AS allocation
    FROM asset_summary a
    JOIN
        current_prices c
    ON
        a.asset = c.asset
)
SELECT
    asset,
    SUM(allocation) AS total_allocation
FROM current_values
GROUP BY asset
ORDER BY total_allocation DESC;
"""

GET_ALLOCATION_BY_PORTFOLIO="""
    WITH latest_portfolio AS (
        SELECT portfolio, MAX(date) as latest_date
        FROM portfolio
        GROUP BY portfolio
    ),
    filtered_portfolio AS (
        SELECT
            p.portfolio,
            p.balance
        FROM portfolio p
        JOIN
            latest_portfolio lp
        ON
            p.portfolio = lp.portfolio AND p.date = lp.latest_date
    ),
    total_balance AS (
        SELECT
            SUM(balance) AS total_portfolios
        FROM filtered_portfolio
    )
    SELECT
        fp.portfolio,
        fp.balance,
        ROUND((fp.balance / tb.total_portfolios) * 100, 2) AS total_allocation
    FROM filtered_portfolio fp
    JOIN
        total_balance tb ON 1=1
    ORDER BY total_allocation DESC;
"""
ADD_NEW_PORTFOLIO = """
    INSERT INTO portfolio (portfolio, total_invested, realised_profit, unrealised_profit, balance, date)
    VALUES (:portfolio, 0, 0, 0, 0, Date('now'))
"""

GET_ALLOCATION="""
    WITH asset_summary AS (
        SELECT 
            {filter}, 
            asset, 
            SUM(CASE WHEN action = 'BUY' THEN amount ELSE -amount END) AS amount_holdings
        FROM asset_transaction
        GROUP BY {filter}, asset
    ),
    current_values AS (
        SELECT 
            a.{filter}, 
            a.asset, 
            a.amount_holdings, 
            c.current_price, 
            a.amount_holdings * c.current_price AS allocation
        FROM asset_summary a
        JOIN current_prices c ON a.asset = c.asset
    )
    SELECT 
        {filter}, 
        SUM(allocation) AS total_allocation
    FROM current_values
    GROUP BY {filter}
    ORDER BY total_allocation DESC;
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
GET_HISTORY_BY_PORTFOLIO = """
    SELECT date as Date, balance AS Value
    FROM portfolio
    WHERE portfolio = :portfolio
    ORDER BY date;
"""

GET_HISTORY_OVERVIEW = """
    SELECT date as Date, SUM(balance) AS Value
    FROM portfolio
    GROUP BY date
    ORDER BY date;
"""

UPDATE_TRANSACTIONS_PORTFOLIO = """
    UPDATE asset_transaction
    SET Portfolio = :Portfolio
    WHERE Date = :Date and Time_UTC_ = :Time_UTC_ and Asset = :Asset
"""


GET_PORTFOLIOS_LIST = "SELECT DISTINCT portfolio FROM portfolio"

GET_ALL_TRANSACTIONS = "SELECT * FROM asset_transaction"

GET_ASSETS = "SELECT * FROM asset"

GET_HOLDINGS_DATA = """
    WITH asset_summary AS (
        SELECT
            Portfolio,
            Asset,
            SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE -Amount END) AS amount_holdings,
            SUM(CASE WHEN Action = 'BUY' THEN Cost ELSE 0 END) AS total_invested,
            SUM(CASE WHEN Action = 'SELL' THEN (Price * Amount - Fee_Cost) ELSE 0 END) AS realised_profit
        FROM
            asset_transaction
        WHERE Portfolio = :portfolio
        GROUP BY
            Portfolio,Asset   
    )
    SELECT
        a.Asset,
        cp.Current_Price,
        a.amount_holdings AS Amount,
        a.amount_holdings * cp.current_price AS Balance,
        a.total_invested,
        a.total_invested / a.amount_holdings AS Average_Buy_Price,
        (a.amount_holdings * cp.current_price) - a.total_invested AS Total_Profit,
        a.realised_profit,
        ((a.amount_holdings * cp.current_price) - a.total_invested) - a.realised_profit AS Unrealised_Profit
    FROM
        asset_summary a
    JOIN
        current_prices cp
    ON
        a.Asset = cp.Asset
"""


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
    INSERT INTO asset (Asset, Current_Price, Amount, Balance, Total_Invested, Average_Buy_Price,
        Realised_Profit, Unrealised_Profit, Total_Profit)
    VALUES (:asset, :current_price, :amount, :balance, :total_invested, :avg_buy_price, :realised_profit, :unrealised_profit, :total_profit)
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
final_metrics AS (
    SELECT
        s.Asset,
        c.current_price,
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
    balance, --ABS(RANDOM() % 90001 + balance) AS random_balance
    DATE('now') --DATE('now', printf('-%d days', ABS(RANDOM() % (365 * 5)))) AS random_date
FROM final_metrics;
"""
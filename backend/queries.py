CREATE_TRANSACTIONS="""
CREATE TABLE IF NOT EXISTS Asset_Transaction  (
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
CREATE TABLE IF NOT EXISTS Asset (
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
CREATE TABLE IF NOT EXISTS Portfolio (
    Portfolio TEXT NOT NULL,
    Total_Invested REAL NOT NULL,
    Realised_Profit REAL NOT NULL,
    Unrealised_Profit REAL NOT NULL,
    Balance REAL NOT NULL,
    Date DATE NOT NULL,
    PRIMARY KEY (Portfolio, Date)
);
"""

CREATE_ASSET_PRICE="""
CREATE TABLE IF NOT EXISTS Current_prices  (
    Asset TEXT PRIMARY KEY,
    Current_Price REAL NOT NULL
);
"""



DELETE_ASSET_PRICE="""
    DELETE FROM Current_prices;
"""

GET_ALLOCATION_BY_ASSET="""
WITH asset_summary AS (
    SELECT
        Asset,
        SUM(CASE WHEN action = 'BUY' THEN Amount ELSE -Amount END) AS Amount_Holdings
    FROM Asset_Transaction
    GROUP BY Asset
),
current_values AS (
    SELECT
        a.Asset,
        a.Amount_Holdings,
        c.Current_Price,
        a.Amount_Holdings * c.Current_Price AS Allocation
    FROM asset_summary a
    JOIN
        Current_prices c
    ON
        a.Asset = c.Asset
)
SELECT
    Asset,
    SUM(Allocation) AS Total_Allocation
FROM current_values
GROUP BY Asset
ORDER BY Total_Allocation DESC;
"""

GET_ALLOCATION_BY_PORTFOLIO="""
    SELECT Portfolio, Balance, Total_Allocation
    FROM (
        SELECT Portfolio, Balance, 
               RANK() OVER (ORDER BY Balance DESC) as rank
        FROM Portfolio
"""

GET_ALLOCATION_BY_PORTFOLIO_bak="""
    WITH latest_portfolio AS (
        SELECT Portfolio, MAX(Date) as latest_date
        FROM Portfolio
        GROUP BY Portfolio
    ),
    filtered_portfolio AS (
        SELECT
            p.Portfolio,
            p.Balance
        FROM Portfolio p
        JOIN
            latest_portfolio lp
        ON
            p.Portfolio = lp.Portfolio AND p.Date = lp.latest_date
    ),
    total_balance AS (
        SELECT
            SUM(Balance) AS total_portfolios
        FROM filtered_portfolio
    )
    SELECT
        fp.Portfolio,
        fp.Balance,
        ROUND((fp.Balance / tb.total_portfolios) * 100, 2) AS Total_Allocation
    FROM filtered_portfolio fp
    JOIN
        total_balance tb ON 1=1
    ORDER BY Total_Allocation DESC;
"""

ADD_NEW_PORTFOLIO = """
    INSERT INTO Portfolio (Portfolio, Total_Invested, Realised_Profit, Unrealised_Profit, Balance, Date)
    VALUES (:Portfolio, 0, 0, 0, 0, 0)
"""

ADD_NEW_TRANSACTION = """
    INSERT INTO Asset_Transaction (Date, Time_UTC_, Asset, Action, Price, Amount, Cost, Fee, Fee_Cost, Fee_Coin, Currency, Type, Platform, Portfolio)
    VALUES (:Date, :Time_UTC_, :Asset, :Action, :Price, :Amount, :Cost, :Fee, :Fee_Cost, :Fee_Coin, :Currency, :Type, :Platform, :Portfolio)
"""

GET_ALLOCATION="""
    WITH asset_summary AS (
        SELECT 
            {filter}, 
            Asset, 
            SUM(CASE WHEN action = 'BUY' THEN Amount ELSE -Amount END) AS Amount_Holdings
        FROM Asset_Transaction
        GROUP BY {filter}, Asset
    ),
    current_values AS (
        SELECT 
            a.{filter}, 
            a.Asset, 
            a.Amount_Holdings, 
            c.Current_Price, 
            a.Amount_Holdings * c.Current_Price AS Allocation
        FROM asset_summary a
        JOIN Current_prices c ON a.Asset = c.Asset
    )
    SELECT 
        {filter}, 
        SUM(Allocation) AS Total_Allocation
    FROM current_values
    GROUP BY {filter}
    ORDER BY Total_Allocation DESC;
"""

GET_PORTFOLIO_LATEST_DATA = """
    SELECT p.*
    FROM Portfolio p
    JOIN (
        SELECT Portfolio, MAX(Date) AS max_date
        FROM Portfolio
        GROUP BY Portfolio
    ) latest ON p.Portfolio = latest.Portfolio AND p.Date = latest.max_date;
"""

GET_HISTORY_BY_PORTFOLIO = """
    SELECT Date as Date, Balance AS Value
    FROM Portfolio
    WHERE Portfolio = :Portfolio
    ORDER BY Date;
"""

GET_PORTFOLIO_HISTORY_OVERVIEW = """
    SELECT Date, SUM(Balance) AS total_balance
    FROM Portfolio
    WHERE Date != 0
    GROUP BY Date
    ORDER BY Date;
"""

UPDATE_TRANSACTIONS_PORTFOLIO = """
    UPDATE Asset_Transaction
    SET Portfolio = :Portfolio
    WHERE Date = :Date and Time_UTC_ = :Time_UTC_ and Asset = :Asset
"""

GET_PORTFOLIO_HISTORY = "SELECT * FROM Portfolio WHERE Portfolio = :Portfolio AND Date != 0 ORDER BY Date"

GET_ALL_PORTFOLIOS = "SELECT * FROM Portfolio ORDER BY Date"

GET_PORTFOLIOS_LIST = "SELECT DISTINCT Portfolio FROM Portfolio"

GET_ALL_TRANSACTIONS = "SELECT * FROM Asset_Transaction"

GET_ALL_ASSETS = "SELECT * FROM Asset"

GET_ASSETS_BY_PORTFOLIO = """
    SELECT * FROM Asset
    WHERE Asset IN (SELECT Asset FROM Asset_Transaction WHERE Portfolio = :Portfolio)
"""

GET_PORTFOLIO_ALLOCATION = """
    SELECT Portfolio, Balance, Total_Allocation
    FROM (
        SELECT Portfolio, Balance, 
               RANK() OVER (ORDER BY Balance DESC) as rank
        FROM Portfolio
    )
"""


GET_HOLDINGS_DATA = """
    WITH asset_summary AS (
        SELECT
            Portfolio,
            Asset,
            SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE -Amount END) AS Amount_Holdings,
            SUM(CASE WHEN Action = 'BUY' THEN Cost ELSE 0 END) AS Total_Invested,
            SUM(CASE WHEN Action = 'SELL' THEN (Price * Amount - Fee_Cost) ELSE 0 END) AS Realised_Profit
        FROM
            Asset_Transaction
        WHERE Portfolio = :Portfolio AND Amount_Holdings != 0
        GROUP BY
            Portfolio,Asset   
    )
    SELECT
        a.Asset,
        cp.Current_Price,
        a.Amount_Holdings AS Amount,
        a.Amount_Holdings * cp.Current_Price AS Balance,
        a.Total_Invested,
        a.Total_Invested / a.Amount_Holdings AS Average_Buy_Price,
        (a.Amount_Holdings * cp.Current_Price) - a.Total_Invested AS Total_Profit,
        a.Realised_Profit,
        ((a.Amount_Holdings * cp.Current_Price) - a.Total_Invested) - a.Realised_Profit AS Unrealised_Profit
    FROM
        asset_summary a
    JOIN
        Current_prices cp
    ON
        a.Asset = cp.Asset
"""



GET_TRANSACTIONS_BY_PORTFOLIO = """
    SELECT * 
    FROM Asset_Transaction
    WHERE Portfolio = ?
"""

COUNT_ASSETS ="""
SELECT COUNT(*) FROM Asset WHERE Asset = :Asset
"""

COUNT_ASSET_PRICE ="""
    SELECT COUNT(*) FROM Current_prices WHERE Asset = :Asset
"""

INSERT_ASSET_PRICE ="""
    INSERT INTO Current_prices (Asset,Current_Price)
    VALUES (:Asset, :Current_Price)
"""

UPDATE_ASSETS ="""
    UPDATE Asset
    SET Amount = :Amount, Balance = :Balance, Total_Invested = :Total_Invested, Average_Buy_Price = :avg_buy_price,
        Current_Price = :Current_Price, Realised_Profit = :Realised_Profit, Unrealised_Profit = :Unrealised_Profit, Total_Profit = :Total_Profit
    WHERE Asset = :Asset
"""

INSERT_ASSETS ="""
    INSERT INTO Asset (Asset, Current_Price, Amount, Balance, Total_Invested, Average_Buy_Price,
        Realised_Profit, Unrealised_Profit, Total_Profit)
    VALUES (:Asset, :Current_Price, :Amount, :Balance, :Total_Invested, :avg_buy_price, :Realised_Profit, :Unrealised_Profit, :Total_Profit)
"""

CALCULATE_ASSET_METRICS = """
WITH asset_summary AS (
    SELECT
        Asset,
        SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE -Amount END) AS Amount,
        SUM(CASE WHEN Action = 'SELL' THEN Amount * Price - Fee_Cost ELSE 0 END) AS Realised_Profit,
        SUM(CASE WHEN Action = 'BUY' THEN Cost ELSE -(Amount * Price - Fee_Cost) END) AS Total_Invested
    FROM Asset_Transaction
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
    FROM Asset_Transaction
    GROUP BY Asset
),
final_metrics AS (
    SELECT
        s.Asset,
        c.Current_Price,
        s.Amount,
        s.Amount * c.Current_Price AS Balance,
        s.Total_Invested,
        a.average_buy_price,
        s.Realised_Profit,
        (s.Amount * c.Current_Price) - (s.Total_Invested) AS Unrealised_Profit,
        ((s.Amount * c.Current_Price) - (s.Total_Invested)) + s.Realised_Profit AS total_profit
    FROM asset_summary s
    JOIN average_buy_price a ON s.Asset = a.Asset
    JOIN Current_prices c ON s.Asset = c.Asset
)
SELECT * FROM final_metrics;
"""

SAVE_PORTFOLIO_METRICS = """
WITH transaction_months AS (
    SELECT DISTINCT
        Portfolio,
        strftime('%Y-%m', Date) AS transaction_month
    FROM Asset_Transaction
),
filtered_transactions AS (
    SELECT
        at.*,
        tm.transaction_month
    FROM Asset_Transaction at
    JOIN transaction_months tm
        ON at.Portfolio = tm.Portfolio
        AND strftime('%Y-%m', at.Date) <= tm.transaction_month
),
asset_summary AS (
    SELECT
        Portfolio,
        Asset,
        transaction_month,
        SUM(CASE WHEN action = 'BUY' THEN Amount ELSE -Amount END) AS Amount_Holdings,
        SUM(CASE WHEN action = 'BUY' THEN cost ELSE 0 END) AS total_buy_cost,
        SUM(CASE WHEN action = 'SELL' THEN Amount * price - fee_cost ELSE 0 END) AS Realised_Profit
    FROM filtered_transactions
    GROUP BY Portfolio, Asset, transaction_month
),
current_values AS (
    SELECT
        a.Portfolio,
        a.Asset,
        a.transaction_month,
        a.Amount_Holdings,
        a.total_buy_cost,
        a.Realised_Profit,
        c.Current_Price,
        a.Amount_Holdings * c.Current_Price AS Balance
    FROM asset_summary a
    JOIN Current_prices c ON a.Asset = c.Asset
),
final_metrics AS (
    SELECT
        Portfolio,
        transaction_month,
        SUM(total_buy_cost - Realised_Profit) AS Total_Invested,
        SUM(Realised_Profit) AS Realised_Profit,
        SUM(Balance - (total_buy_cost - Realised_Profit)) AS Unrealised_Profit,
        SUM(Balance) AS Balance
    FROM current_values
    GROUP BY Portfolio, transaction_month
)
INSERT OR REPLACE INTO Portfolio (Portfolio, Total_Invested, Realised_Profit, Unrealised_Profit, Balance, Date)
SELECT 
    fm.Portfolio, 
    fm.Total_Invested, 
    fm.Realised_Profit, 
    fm.Unrealised_Profit, 
    fm.Balance,
    fm.transaction_month || '-01' AS Date -- Use the first day of the month as the Date
FROM final_metrics fm;
"""


SAVE_PORTFOLIO_METRICS_bak2 = """
WITH asset_summary AS (
    SELECT
        Portfolio,
        Asset,
        SUM(CASE WHEN action = 'BUY' THEN Amount ELSE -Amount END) AS Amount_Holdings,
        SUM(CASE WHEN action = 'BUY' THEN cost ELSE 0 END) AS total_buy_cost,
        SUM(CASE WHEN action = 'SELL' THEN Amount * price - fee_cost ELSE 0 END) AS Realised_Profit
    FROM Asset_Transaction
    GROUP BY Portfolio, Asset
),
current_values AS (
    SELECT
        a.Portfolio,
        a.Asset,
        a.Amount_Holdings,
        a.total_buy_cost,
        a.Realised_Profit,
        c.Current_Price,
        a.Amount_Holdings * c.Current_Price AS Balance
    FROM asset_summary a
    JOIN Current_prices c ON a.Asset = c.Asset
),
final_metrics AS (
    SELECT
        Portfolio,
        SUM(total_buy_cost - Realised_Profit) AS Total_Invested,
        SUM(Realised_Profit) AS Realised_Profit,
        SUM(Balance - (total_buy_cost - Realised_Profit)) AS Unrealised_Profit,
        SUM(Balance) AS Balance
    FROM current_values
    GROUP BY Portfolio
),
transaction_months AS (
    SELECT DISTINCT
        Portfolio,
        strftime('%Y-%m', Date) AS transaction_month
    FROM Asset_Transaction
)
INSERT OR REPLACE INTO Portfolio (Portfolio, Total_Invested, Realised_Profit, Unrealised_Profit, Balance, Date)
SELECT 
    fm.Portfolio, 
    fm.Total_Invested, 
    fm.Realised_Profit, 
    fm.Unrealised_Profit, 
    fm.Balance,
    tm.transaction_month || '-01' AS Date -- Use the first day of the month as the Date
FROM final_metrics fm
JOIN transaction_months tm ON fm.Portfolio = tm.Portfolio;
"""

SAVE_PORTFOLIO_METRICS_bak = """
WITH asset_summary AS (
    SELECT
        Portfolio,
        Asset,
        SUM(CASE WHEN action = 'BUY' THEN Amount ELSE -Amount END) AS Amount_Holdings,
        SUM(CASE WHEN action = 'BUY' THEN cost ELSE 0 END) AS total_buy_cost,
        SUM(CASE WHEN action = 'SELL' THEN Amount * price - fee_cost ELSE 0 END) AS Realised_Profit
    FROM Asset_Transaction
    GROUP BY Portfolio, Asset
),
current_values AS (
    SELECT
        a.Portfolio,
        a.Asset,
        a.Amount_Holdings,
        a.total_buy_cost,
        a.Realised_Profit,
        c.Current_Price,
        a.Amount_Holdings * c.Current_Price AS Balance
    FROM asset_summary a
    JOIN Current_prices c ON a.Asset = c.Asset
),
final_metrics AS (
    SELECT
        Portfolio,
        SUM(total_buy_cost - Realised_Profit) AS Total_Invested,
        SUM(Realised_Profit) AS Realised_Profit,
        SUM(Balance - (total_buy_cost - Realised_Profit)) AS Unrealised_Profit,
        SUM(Balance) AS Balance
    FROM current_values
    GROUP BY Portfolio
)
INSERT OR REPLACE INTO Portfolio (Portfolio, Total_Invested, Realised_Profit, Unrealised_Profit, Balance, Date)
SELECT 
    Portfolio, 
    Total_Invested, 
    Realised_Profit, 
    Unrealised_Profit, 
    Balance, --ABS(RANDOM() % 90001 + Balance) AS random_balance
    DATE('now') --DATE('now', printf('-%d days', ABS(RANDOM() % (365 * 5)))) AS random_date
FROM final_metrics;
"""
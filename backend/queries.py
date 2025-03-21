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

ADD_NEW_PORTFOLIO = """
    INSERT INTO Portfolio (Portfolio, Total_Invested, Realised_Profit, Unrealised_Profit, Balance, Date)
    VALUES (:Portfolio, 0, 0, 0, 0, 0)
"""

ADD_NEW_TRANSACTION = """
    INSERT INTO Asset_Transaction (Date, Time_UTC_, Asset, Action, Price, Amount, Cost, Fee, Fee_Cost, Fee_Coin, Currency, Type, Platform, Portfolio)
    VALUES (:Date, :Time_UTC_, :Asset, :Action, :Price, :Amount, :Cost, :Fee, :Fee_Cost, :Fee_Coin, :Currency, :Type, :Platform, :Portfolio)
"""

GET_ASSETS_BY ="""
WITH holdings_by_allocation AS (
    SELECT  
        Asset,
        {filter},
        SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE -Amount END) AS Amount_Holdings
    FROM Asset_Transaction
    GROUP BY {filter}, Asset
)
SELECT h.Asset, h.{filter}, h.Amount_Holdings, h.Amount_Holdings * c.Current_Price AS Balance
FROM holdings_by_allocation h
JOIN Current_prices c ON h.Asset = c.Asset
WHERE h.Amount_Holdings > 0
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

GET_PORTFOLIO_HISTORY_OVERVIEW = """
    SELECT Date, SUM(Balance) AS total_balance
    FROM Portfolio
    WHERE Date != 0
    GROUP BY Date
    ORDER BY Date;
"""

GET_PORTFOLIO_HISTORY = "SELECT * FROM Portfolio WHERE Portfolio = :Portfolio AND Date != 0 ORDER BY Date"


GET_PORTFOLIOS_LIST = "SELECT DISTINCT Portfolio FROM Portfolio"

GET_ALL_TRANSACTIONS = "SELECT * FROM Asset_Transaction"

GET_ALL_ASSETS = """
    SELECT Asset,Amount,Total_Invested, Current_Price, Balance, Average_Buy_Price,Realised_Profit,Unrealised_Profit,Total_Profit 
    FROM Asset WHERE Amount > 0
"""

GET_ASSETS_BY_PORTFOLIO = """
    SELECT a.Asset,a.Amount,a.Total_Invested, a.Current_Price,a.Balance, a.Average_Buy_Price,a.Realised_Profit,a.Unrealised_Profit,a.Total_Profit
    FROM Asset a
    JOIN Asset_Transaction ON a.Asset = Asset_Transaction.Asset
    WHERE Asset_Transaction.Portfolio = :Portfolio AND a.Amount > 0
    GROUP BY a.Asset
"""

GET_HOLDINGS_DATA = """
    WITH asset_summary AS (
        SELECT
            Portfolio,
            Asset,
            -- Total amount holding (buys - sells)
            SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE -Amount END) AS Amount_Holdings,
            
            -- Total cost of buys
            SUM(CASE WHEN Action = 'BUY' THEN Cost ELSE 0 END) AS Total_Invested,
            
            -- Realized profit from sells (selling price - fees)
            SUM(CASE WHEN Action = 'SELL' THEN (Price * Amount - Fee_Cost) ELSE 0 END) AS Realised_Profit
        FROM Asset_Transaction
        WHERE Portfolio = :Portfolio
        GROUP BY Portfolio, Asset
        HAVING Amount_Holdings > 0
    ),
    average_buy_price AS (
        -- Calculate average buy price per portfolio and asset
        SELECT
            Portfolio,
            Asset,
            CASE 
                WHEN SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE 0 END) > 0
                THEN SUM(CASE WHEN Action = 'BUY' THEN Amount * Price ELSE 0 END) / 
                     SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE 0 END)
                ELSE 0
            END AS Average_Buy_Price
        FROM Asset_Transaction
        WHERE Portfolio = :Portfolio
        GROUP BY Portfolio, Asset
    ),
    portfolio_total AS (
        SELECT
            Portfolio,
            SUM(Amount_Holdings * cp.Current_Price) as Total_Balance
        FROM asset_summary a
        JOIN Current_prices cp ON a.Asset = cp.Asset
        GROUP BY Portfolio
    )
    SELECT
        s.Asset,
        cp.Current_Price,                                           -- Current price
        s.Amount_Holdings AS Amount,                                -- Quantity holding
        s.Amount_Holdings * cp.Current_Price AS Balance,           -- Current value
        s.Total_Invested,                                         -- Total cost invested
        a.Average_Buy_Price,                                      -- Average buy price
        s.Realised_Profit,                                       -- Realized profit
        (s.Amount_Holdings * cp.Current_Price) - s.Total_Invested AS Unrealised_Profit,  -- Unrealized profit
        ((s.Amount_Holdings * cp.Current_Price) - s.Total_Invested) + s.Realised_Profit AS Total_Profit,  -- Total profit
        ROUND((s.Amount_Holdings * cp.Current_Price) / NULLIF(pt.Total_Balance, 0) * 100, 2) AS Allocation  -- Allocation percentage
    FROM asset_summary s
    JOIN average_buy_price a ON s.Asset = a.Asset AND s.Portfolio = a.Portfolio
    JOIN Current_prices cp ON s.Asset = cp.Asset
    JOIN portfolio_total pt ON s.Portfolio = pt.Portfolio
    ORDER BY Balance DESC;
"""


GET_TRANSACTIONS_BY_PORTFOLIO = """
    SELECT * 
    FROM Asset_Transaction
    WHERE Portfolio = ?
"""

COUNT_ASSETS ="""
SELECT COUNT(*) FROM Asset WHERE Asset = :Asset
"""

INSERT_ASSET_PRICE ="""
    INSERT INTO Current_prices (Asset,Current_Price)
    VALUES (:Asset, :Current_Price)
"""

UPDATE_ASSETS ="""
    UPDATE Asset
    SET Asset= :Asset ,Amount= :Amount,Total_Invested= :Total_Invested, Current_Price= :Current_Price,Balance= :Balance, Average_Buy_Price= :Average_Buy_Price,Realised_Profit= :Realised_Profit,Unrealised_Profit= :Unrealised_Profit,Total_Profit= :Total_Profit
    WHERE Asset = :Asset
"""

INSERT_ASSETS ="""
    INSERT INTO Asset (Asset,Amount,Total_Invested, Current_Price,Balance, Average_Buy_Price,Realised_Profit,Unrealised_Profit,Total_Profit)
    VALUES (:Asset,:Amount,:Total_Invested, :Current_Price,:Balance, :Average_Buy_Price,:Realised_Profit,:Unrealised_Profit,:Total_Profit)
"""


CALCULATE_HOLDINGS_TABLE = """
WITH asset_summary AS (
    SELECT
        Asset,
        SUM(CASE WHEN Action = 'BUY' THEN Amount ELSE -Amount END) AS Amount_Holdings,
        SUM(CASE WHEN Action = 'BUY' THEN Cost ELSE 0 END) AS Total_Invested,
        SUM(CASE WHEN Action = 'SELL' THEN Amount * Price - Fee_Cost ELSE 0 END) AS Realised_Profit
    FROM Asset_Transaction
    GROUP BY Asset
),
asset_metrics AS (
    SELECT
        a.Asset,
        a.Amount_Holdings,
        a.Total_Invested,
        a.Realised_Profit,
        c.Current_Price,
        a.Total_Invested / NULLIF(a.Amount_Holdings, 0) AS Average_Buy_Price,
        a.Amount_Holdings * c.Current_Price AS Balance,
        (a.Amount_Holdings * c.Current_Price) - a.Total_Invested AS Unrealised_Profit
    FROM asset_summary a
    JOIN Current_prices c ON a.Asset = c.Asset
)
SELECT
    Asset,
    Amount_Holdings AS Amount,
    Total_Invested,
    Current_Price,
    Balance,
    Average_Buy_Price,
    Realised_Profit,
    Unrealised_Profit,
    (Realised_Profit + Unrealised_Profit) AS Total_Profit
FROM asset_metrics;
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
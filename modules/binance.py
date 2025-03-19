import pandas as pd


from utils import logger
from datetime import datetime

def rename_columns(df, column_mapper):

    existing_columns = {k: v for k, v in column_mapper.items() if k in df.columns}
    missing_columns = [k for k in column_mapper if k not in df.columns]

    if missing_columns:
        logger.warning(f"⚠️ Columns not found for renaming: {missing_columns}")

    return df.rename(columns=existing_columns)


def clean_data(df):
    column_mapper = {
        'Date(UTC)': 'Date',
        'Type': 'Action',
        'Market': 'Asset',
        'Total': 'Cost',
        'Fee Coin': 'Fee_Coin'
    }

    df = rename_columns(df, column_mapper)
    #df = df.rename(mapper=column_mapper, axis=1)
    
    pattern = r'([A-Z]+)(USDT|USDC|USD|EURI|EUR)'

    df[['Date', 'Time_UTC_']] = df['Date'].astype(str).str.split(' ', expand=True)    
    df[['Asset','Currency']] = df['Asset'].str.extract(pattern)
    df['Type'] = 'CRYPTO'

    #df = df.astype({'Asset': 'category', 'Price': 'float64', 'Amount':'float64', 'Cost': 'float64', 'Fee': 'float64','Platform':'category'})

    df[['Amount','Price','Cost','Fee']] = df[['Amount','Price','Cost','Fee']].round(8)
    df['Fee_Cost'] = df['Price'] * df['Fee']

    #Fix exchange errors on .csv (price of the asset)
    if df['Fee_Cost'].any() == df['Cost'].any():
        df['Price'] = df['Cost'] / df['Amount']
        df['Fee_Cost'] = df['Fee'] * df['Price']

    return df
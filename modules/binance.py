import pandas as pd
from utils import logger
from utils.logger import logger

def rename_columns(df, column_mapper):

    existing_columns = {k: v for k, v in column_mapper.items() if k in df.columns}
    missing_columns = [k for k in column_mapper if k not in df.columns]

    if missing_columns:
        logger.warning(f"⚠️ Columns not found for renaming: {missing_columns}")

    return df.rename(columns=existing_columns)


def clean_data(df):
    column_mapper = {
        'Type': 'Action',
        'Base Asset': 'Asset',
        'Quote Asset': 'Currency',
        'Total': 'Cost',
        'Fee Coin': 'Fee_Coin'
    }

    df = rename_columns(df, column_mapper)
    
    #pattern = r'([A-Z]+)(USDT|USDC|USD|EURI|EUR)'

    df[['Date', 'Time_UTC_']] = df['Date(UTC)'].astype(str).str.split(' ', expand=True)    

    df = df.drop(['Date(UTC)', 'Pair'], axis=1)
    
    df['Type'] = 'CRYPTO'

    df[['Amount','Price','Cost','Fee']] = df[['Amount','Price','Cost','Fee']].round(8)
    df['Fee_Cost'] = df['Price'] * df['Fee']

    #Fix exchange errors on .csv (price of the asset)
    if df['Fee_Cost'].any() == df['Cost'].any():
        df['Price'] = df['Cost'] / df['Amount']
        df['Fee_Cost'] = df['Fee'] * df['Price']

    return df
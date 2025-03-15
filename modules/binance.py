from datetime import datetime

import pandas as pd


def clean_data_order(df):
    drop_columns = ['OrderNo', 'Order Price','Trigger Condition', 'Filled', 'status']
    df = df.drop(labels=drop_columns, axis=1)

    column_mapper = {
        'Date(UTC)': 'Date',
        'Pair': 'Asset',
        'AvgTrading Price': 'Price',
        'Order Amount': 'Amount',
        'Total': 'Cost'
    }

    df = df.rename(mapper=column_mapper, axis=1)

    df.columns = df.columns.str.title()

    pattern = r'([A-Z]+)(USDT|USDC|USD|EURI|EUR)'

    df[['Asset','Currency']] = df['Asset'].str.extract(pattern)

    # Convert the column to datetime (Pandas will handle any format discrepancies)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Date'] = df['Date'].dt.strftime("%d/%m/%Y")

    df[['Amount','Price','Total']] = df[['Amount','Price','Total']].round(8)

    return df

def clean_data(df):
    column_mapper = {
        'Date(UTC)': 'Date',
        'Market': 'Asset',
        'Total': 'Cost'
    }

    print(df)
    df = df.rename(mapper=column_mapper, axis=1)
    pattern = r'([A-Z]+)(USDT|USDC|USD|EURI|EUR)'


    df[['Date', 'Time(UTC)']] = df['Date'].astype(str).str.split(' ', expand=True)
    # Extract year and month for filtering
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Date'] = df['Date'].dt.date

    df[['Asset','Currency']] = df['Asset'].str.extract(pattern)

    #df = df.astype({'Asset': 'category', 'Price': 'float64', 'Amount':'float64', 'Cost': 'float64', 'Fee': 'float64','Platform':'category'})

    df[['Amount','Price','Cost','Fee']] = df[['Amount','Price','Cost','Fee']].round(8)
    df['Fee Cost'] = df['Price'] * df['Fee']

    #Fix exchange errors on .csv (price of the asset)
    if df['Fee Cost'].any() == df['Cost'].any():
        df['Price'] = df['Cost'] / df['Amount']
        df['Fee Cost'] = df['Fee'] * df['Price']

    return df

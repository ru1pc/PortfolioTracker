
import os.path
import pandas as pd
from utils.logger import logger 
import openpyxl

def ensure_directory_exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)


def export_to_csv(df, output_dir, merge=False):

    ensure_directory_exists(output_dir)

    desired_order = ['Date', 'Time(UTC)', 'Asset', 'Type', 'Price', 'Amount', 'Cost', 'Fee', 'Fee Coin',
                     'Fee Cost', 'Currency','Platform','Year','Month']
    
    existing_columns = [col for col in desired_order if col in df.columns]
    missing_columns = [col for col in desired_order if col not in df.columns]

    if missing_columns:
        logger.warning(f"⚠️ Missing columns in DataFrame: {missing_columns}")

    df = df[existing_columns]

    if df.empty:
        logger.warning("⚠️ No data to export.")
        return
    
    if merge:
        file_name = "all_data.xlsx"
        output_path = os.path.join(output_dir, file_name)
        with pd.ExcelWriter(output_path, mode='a' if os.path.exists(output_path) else 'w') as writer:
            df.drop(columns=['Year','Month']).to_excel(writer, index=False)

    else:
        years = df['Year'].unique()
        
        for year in years:
            year_df = df[df['Year'] == year]
            if year_df.empty:
                continue
            
            file_name = f"{year}_report.xlsx"    
            output_path = os.path.join(output_dir, file_name)
            with pd.ExcelWriter(output_path) as writer:
                months = sorted(year_df['Month'].unique())
                for month in months:
                    month_df = year_df[year_df['Month'] == month].drop(columns=['Year', 'Month'])
                    sheet_name = f"{month}"
                    month_df.to_excel(writer, index=False, sheet_name=sheet_name)
            
    logger.info(f"💼 Generated {file_name}")
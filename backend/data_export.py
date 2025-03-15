from utils.logger import logger 
import os.path
import pandas as pd


def ensure_directory_exists(output_dir):
    """
    Ensure the output directory exists. If not, create it.

    Args:
    - output_dir (str): Path to the output directory.
    """
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
    
    years = df['Year'].unique()
    
    for year in years:
        year_df = df[df['Year'] == year]
        if year_df.empty:
            continue

        if not merge:
            file_name = f"{year}_report.xlsx"    
            output_path = os.path.join(output_dir, file_name)
            with pd.ExcelWriter(output_path) as writer:
                months = sorted(year_df['Month'].unique())
                for month in months:
                    month_df = year_df[year_df['Month'] == month].drop(columns=['Year', 'Month'])
                    sheet_name = f"{month}"
                    month_df.to_excel(writer, index=False, sheet_name=sheet_name)
        else:
            file_name = f"{year}_report_merged.xlsx"
            output_path = os.path.join(output_dir, file_name)
            with pd.ExcelWriter(output_path, mode='a' if os.path.exists(output_path) else 'w') as writer:
                year_df.drop(columns=['Year','Month']).to_excel(writer, index=False, sheet_name=f"{year}")
        
        logger.info(f"💼 Generated {file_name}")
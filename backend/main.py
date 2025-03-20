import argparse
import sys, os
import subprocess

 # Add the parent directory of 'modules' to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import backend.data_processing as dp
import backend.data_export as de
import backend.data_persistence as dper 
import backend.database as db 
from utils.logger import logger
import requests

def get_crypto_price(url):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract the content of the response
            price = response.text.strip()  # The price is usually returned as plain text
            price = float(price)
            return price
        else:
            # Handle errors if the request fails
            logger.error(f"Failed to fetch price. Status code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

def asset_current_price(asset):
    price = get_crypto_price(f"https://cryptoprices.cc/{asset}")
    if price is not None:
        return price
    else:
       return 0
     

def ui():
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'app.py')
    logger.info("🚀 Launching Streamlit application...")
    subprocess.run(['streamlit', 'run', frontend_path])

def main(data, output, merge):
    df = dp.load_data_from_folder(data)
    if df is not None:
        dper.initialize_db()
        
        # Get unique assets and create a price dictionary
        unique_assets = df['Asset'].unique()
        asset_prices = {asset: asset_current_price(asset) for asset in unique_assets}
        dper.save_to_db(df, portfolio="default", asset_prices=asset_prices)
        dper.print_table("current_prices")
        dper.print_table("asset")
        logger.info("✅ Data saved to database.")
    else:
        logger.warning("⚠️ No data was loaded.")
        return
    
    ui()
 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Management my investments.")
    parser.add_argument("--data", default="data", help="Data folder for platform data")
    parser.add_argument("--output", default="reports", help="Generate reports in the output folder")
    parser.add_argument("--merge", action='store_true', help="Merge all data in one file")
    args = parser.parse_args()

    main(args.data, args.output, args.merge)

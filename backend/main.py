import argparse
import sys, os
import subprocess
import requests

# Add the parent directory of 'modules' to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from utils.logger import logger

import backend.data_export as de
import backend.data_persistence as dper 
import backend.database as db
import backend.data_processing as dp


def update_asset_prices(assets):
    updated_prices = {}
    for asset in assets:
        price = get_crypto_price(f"https://cryptoprices.cc/{asset}")
        if price is not None:
            updated_prices[asset] = price
    else:
        updated_prices[asset] = 0
    db.save_asset_prices(updated_prices)
    


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
     

def ui():
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'app.py')
    logger.info("🚀 Launching Streamlit application...")
    subprocess.run(['streamlit', 'run', frontend_path])

def main(data, output, merge):
    # Initialize database first
    dper.initialize_db()
    logger.info("✅ Database initialized")
    
    # Try to load and process data if available
    df = dp.load_data_from_folder(data)
    if df is not None:
        # Get unique assets and create a price dictionary
        unique_assets = df['Asset'].unique()
        update_asset_prices(unique_assets)
        dper.save_to_db(df, portfolio="default")
        logger.info("✅ Data saved to database")
    else:
        logger.warning("⚠️ No data was loaded, starting with empty database")
    
    # Launch UI regardless of data presence
    ui()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Management my investments.")
    parser.add_argument("--data", default="data", help="Data folder for platform data")
    parser.add_argument("--output", default="reports", help="Generate reports in the output folder")
    parser.add_argument("--merge", action='store_true', help="Merge all data in one file")
    args = parser.parse_args()

    main(args.data, args.output, args.merge)

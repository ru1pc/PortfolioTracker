import argparse
import sys, os

 # Add the parent directory of 'modules' to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from backend.data_processing import load_all_data
from backend.data_export import export_to_csv
from backend.data_persistence import initialize_db,save_to_db,check_db
from utils.logger import logger

from backend.queries import (
    calculate_total_profit, 
    calculate_realised_profit, 
    calculate_total_invested, 
    calculate_unrealised_profit, 
    calculate_average_buy_price, 
    calculate_balance
)


def asset_metrics(asset_name):
    current_price = 30000  # Exemplo de preço atual do BTC

    print(f"📊 Metrics for {asset_name}:")
    print(f"- Total Profit: ${calculate_total_profit(asset_name, current_price):.2f}")
    print(f"- Realised Profit: ${calculate_realised_profit(asset_name):.2f}")
    print(f"- Total Invested: ${calculate_total_invested(asset_name):.2f}")
    print(f"- Unrealised Profit: ${calculate_unrealised_profit(asset_name, current_price):.2f}")
    print(f"- Average Buy Price: ${calculate_average_buy_price(asset_name):.2f}")
    print(f"- Balance: ${calculate_balance(asset_name, current_price):.2f}")


def main(data, output, merge):
    try:
        df = load_all_data(data)

        if df is not None:
            save_to_db(df)
            logger.info("✅ Data saved to database.")
        else:
            logger.warning("⚠️ No data was loaded.")

        if df is not None:
            logger.info("📊 Data processing complete. Exporting data...")
            export_to_csv(df, output, merge)
        else:
            logger.warning("No data was loaded.")

    except Exception as e:
        logger.error(f"❌ An error occurred: {e}")

    initialize_db(df)

    asset_metrics("BTC")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and export investment data.")
    parser.add_argument("--data", default="data", help="Path to the input data folder")
    parser.add_argument("--output", default="reports", help="Path for outputs")
    parser.add_argument("--merge", action='store_true', help="Merge all data in one file")
    args = parser.parse_args()

    main(args.data,args.output,args.merge)

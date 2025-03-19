import argparse
import sys, os

 # Add the parent directory of 'modules' to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import backend.data_processing as dp
import backend.data_export as de
import backend.data_persistence as dper 
import backend.database as db 

from utils.logger import logger

def get_current_prices():
     current_prices = {
        "ADA": 0.70,
        "ETH": 1914.0,
        "XRP": 0.50
    }
     return current_prices

def main(data, output, merge):
        
        
    #try:
        df = dp.load_all_data(data)
        if df is not None:
            current_prices=get_current_prices()
            dper.initialize_db()
            dper.save_to_db(df,portfolio="default",asset_prices=current_prices)
            #dper.print_table('portfolio')
            logger.info("✅ Data saved to database.")
        else:
            logger.warning("⚠️ No data was loaded.")

    #    if df is not None:
    #        logger.info("📊 Data processing complete. Exporting data...")
    #        export_to_csv(df, output, merge)
    #    else:
    #        logger.warning("No data was loaded.")

    #except Exception as e:
    #    logger.error(f"❌ An error occurred: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Management my investments.")
    parser.add_argument("--data", default="data", help="Path to the input data folder")
    parser.add_argument("--output", default="reports", help="Generate reports in the output folder")
    parser.add_argument("--merge", action='store_true', help="Merge all data in one file")
    args = parser.parse_args()

    main(args.data,args.output,args.merge)

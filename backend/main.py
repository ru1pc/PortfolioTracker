import argparse
import sys, os
from data_processing import load_all_data
from data_export import export_to_csv

# Add the parent directory of 'backend' to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from utils.logger import logger

def main(data, output, merge):
    #try:
        df = load_all_data(data)

        if df is not None:
            logger.info("📊 Data processing complete. Exporting data...")
            export_to_csv(df, output, merge)
        else:
            logger.warning("No data was loaded.")

    #except Exception as e:
    #    logger.error(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and export investment data.")
    parser.add_argument("--data", default="data", help="Path to the input data folder")
    parser.add_argument("--output", default="reports", help="Path for outputs")
    parser.add_argument("--merge", action='store_true', help="Merge all data in one file")
    args = parser.parse_args()

    main(args.data,args.output,args.merge)

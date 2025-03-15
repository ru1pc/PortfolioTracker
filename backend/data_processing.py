import os
import pandas as pd
import importlib


def load_all_data(base_path="data"):
    """
    Load and process all platform data.

    Returns:
    - DataFrame: Consolidated and cleaned data.
    """
    all_data = []
    
    for platform in os.listdir(base_path):
        platform_path = os.path.join(base_path, platform)
        
        if os.path.isdir(platform_path):
            print(f"🔍 Processing data from {platform}...")
            platform_data = load_platform_data(platform_path, platform)
            all_data.extend(platform_data)

    return pd.concat(all_data, ignore_index=True) if all_data else None


def load_platform_data(platform_folder, platform):
    """
    Load all data files from a platform's folder.

    Args:
    - platform_folder (str): Path to the platform's folder (e.g., 'data/binance').
    - platform (str): The platform name (used to import the correct cleaning module).

    Returns:
    - List of DataFrames: Cleaned data for each file in the folder.
    """
    dataframes = []
    
    # check if 'modules' exists
    try:
        data_module = importlib.import_module(f"modules.{platform}")
    except ModuleNotFoundError:
        print(f"⚠️ {platform} not supported.")
        return []

    for file_name in os.listdir(platform_folder):
        file_path = os.path.join(platform_folder, file_name)
        
        if file_path.endswith(('.csv')):
            print(f"📂 Uploading {file_path}")
            df = pd.read_csv(file_path)

            # Process specific platform
            if hasattr(data_module, "clean_data"):
                df = data_module.clean_data(df)
                df["platform"] = platform 
                dataframes.append(df)
            else:
                print(f"⚠️ {platform} do not have 'clean_data' function")

    return dataframes
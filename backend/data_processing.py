﻿import os
import sys
import csv
import pandas as pd
import importlib

# Add the parent directory of 'backend' to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from utils.logger import logger

def detect_delimiter(file_path):
    with open(file_path, 'r') as file:
        sample = file.read(1024)
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter

def normalize_data(df, platform):
  
    expected_columns = ["Date", "Time_UTC_", 'Asset','Type','Action','Price','Amount','Cost','Fee','Fee_Coin','Fee_Cost','Currency']  
    missing_columns = [col for col in expected_columns if col not in df.columns]

    if missing_columns:
        logger.warning(f"⚠️ Missing columns in {platform}: {missing_columns}")
        for col in missing_columns:
            df[col] = None  # Add missing columns with None values

    df["Platform"] = platform  
    return df

def load_data_from_folder(base_path="data"):
  
    if not os.path.exists(base_path):
        logger.error(f"❌ Base path '{base_path}' does not exist.")
        return None
    
    all_data = []
    
    for platform in os.listdir(base_path):
       
        platform_path = os.path.join(base_path, platform)
        if not os.path.isdir(platform_path):
            logger.warning(f"⚠️ Skipping invalid platform folder: {platform_path}")
            continue

        if os.path.isdir(platform_path):
            logger.info(f"🔍 Processing data from {platform}...")
            platform_data = load_platform_data(platform_path, platform)
            all_data.extend(platform_data)

    if all_data:
        return pd.concat(all_data, ignore_index=True,sort=True)
    else:
        logger.warning("⚠️ No data was loaded from any platform.")
        return None

def load_platform_data(platform_folder, platform):

    dataframes = []
    
    # check if 'modules' exists
    try:
        data_module = importlib.import_module(f"modules.{platform}")
    except ModuleNotFoundError as e:
        logger.warning(f"⚠️ {platform} not supported. Error: {e}")
        return []

    for file_name in os.listdir(platform_folder):
        file_path = os.path.join(platform_folder, file_name)
        
        try:
            if file_path.endswith(('.csv', '.xlsx')): 

                if file_path.endswith('.csv'):
                    delimiter = detect_delimiter(file_path)
                    df = pd.read_csv(file_path, sep=delimiter)
                else:
                    df = pd.read_excel(file_path)

                logger.info(f"📂 Uploaded {file_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load file {file_path}: {e}")
            continue  # Skip to the next file
        
        # Process specific platform
        if hasattr(data_module, "clean_data"):
            df = data_module.clean_data(df)
            df = normalize_data(df, platform)
            dataframes.append(df)
        else:
            logger.warning(f"⚠️ {platform} do not have 'clean_data' function")
    
    return dataframes

def load_platform_file(file, platform):
    dataframes = {}

    try:
        data_module = importlib.import_module(f"modules.{platform}")
    except ModuleNotFoundError as e:
        logger.warning(f"⚠️ {platform} not supported. Error: {e}")
        return {}
    
    # Check file extension and read accordingly
    if file.endswith('.csv'):
        delimiter = detect_delimiter(file)
        df = pd.read_csv(file, sep=delimiter)
    elif file.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        logger.warning(f"⚠️ Unsupported file format: {file}")
        return {}

    # Process specific platform
    if hasattr(data_module, "clean_data"):
        df = data_module.clean_data(df)
        df = normalize_data(df, platform)

    else:
        logger.warning(f"⚠️ {platform} do not have 'clean_data' function")
    return df
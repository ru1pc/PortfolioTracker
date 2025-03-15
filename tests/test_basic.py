import os
import pandas as pd
from backend.data_export import export_to_csv
from backend.data_processing import load_all_data

def test_load_all_data():
 
    mock_data = pd.DataFrame({
        "Date": ["2023-01-01"],
        "Asset": ["BTC"],
        "Amount": [1.0],
        "Cost": [20000.0]
    })
    mock_data.to_csv("tests/mock_data.csv", index=False)

    # Testa a função load_all_data
    df = load_all_data(base_path="tests/")
    assert df is not None
    assert len(df) == 1
    assert df.iloc[0]["Asset"] == "BTC"

def test_export_to_csv():
    df = pd.DataFrame({
        "Date": ["2023-01-01"],
        "Asset": ["BTC"],
        "Amount": [1.0],
        "Cost": [20000.0],
        "Year": [2023],
        "Month": [1]
    })
    export_to_csv(df, output_dir="tests/output", merge=True)
    assert os.path.exists("tests/output/merged_2023.xlsx")
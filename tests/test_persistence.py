import pandas as pd
from backend.data_persistence import save_to_db, load_from_db

def test_save_and_load():
    df = pd.DataFrame({
        "Date": ["2023-01-01"],
        "Asset": ["BTC"],
        "Amount": [1.0],
        "Cost": [20000.0],
        "Platform": ["Binance"],
        "Year": [2023],
        "Month": [1]
    })

    # Save data to database
    save_to_db(df)

    # Load data from database
    loaded_df = load_from_db()
    assert not loaded_df.empty
    assert loaded_df.iloc[0]["Asset"] == "BTC"
from data_processing import load_all_data


OUTPUT_FILE = "processed_data.csv"  # Define the output file name

def main():
    df = load_all_data()

    if df is not None:
            print("📊 Data processing complete. Exporting to CSV...")
            df.to_csv(OUTPUT_FILE, index=False)  # Save to CSV without the index column
            print(f"✅ Processed data saved to {OUTPUT_FILE}")
        else:
            print("⚠️ No data was loaded.")

if __name__ == "__main__":
    main()

# skirpta za stvaranje csv tablica za redovne i izvanredne ubacivanja i izbacivanja

import pandas as pd
import re

def process_market_data(file_path):
    # Load the Excel file
    # Note: If your file has multiple sheets, add sheet_name='Sheet1'
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading the file: {e}")
        return

    def clean_and_split(df_source, ticker_col, event_label):
        # 1. Filter by event type (Regular vs Irregular)
        # Using .str.contains to handle potential extra spaces or case differences
        mask = df_source['redovna / izvanredna'].astype(str).str.strip().str.lower() == event_label.lower()
        subset = df_source[mask].copy()

        # 2. Rename columns for the final CSV format
        subset = subset[['Datum objave', 'Prvi dan trgovanja nakon provedbe', ticker_col]]
        subset.columns = ['AnnDate', 'EventDate', 'Symbol']

        # 3. Handle Dates
        # Format 'dd.mm.yyyy.' is parsed specifically here
        for col in ['AnnDate', 'EventDate']:
            # We use dayfirst=True and errors='coerce' to handle the dots gracefully
            subset[col] = pd.to_datetime(subset[col], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

        # 4. Process Ticker Symbols
        # Drop empty symbol rows, split by semicolon, and explode into individual rows
        subset = subset.dropna(subset=['Symbol'])
        subset['Symbol'] = subset['Symbol'].astype(str).str.split(';')
        subset = subset.explode('Symbol')

        # 5. Clean Symbols
        # Trim whitespace and remove '-R-A' from the end (case-insensitive)
        subset['Symbol'] = subset['Symbol'].str.strip()
        subset['Symbol'] = subset['Symbol'].str.replace(r'-R-A$', '', regex=True, flags=re.IGNORECASE)
        
        # Remove any rows that ended up with an empty symbol
        subset = subset[subset['Symbol'] != ""]

        # 6. Final Column Selection
        return subset[['Symbol', 'AnnDate', 'EventDate']]

    # Mapping configurations: (Source Column, Event Type Filter, Target Filename)
    configs = [
        ("Uključeni", "redovna", "regular_added.csv"),
        ("Uključeni", "izvanredna", "irregular_added.csv"),
        ("Isključeni", "redovna", "regular_deleted.csv"),
        ("Isključeni", "izvanredna", "irregular_deleted.csv")
    ]

    # Generate the files
    for src_col, event_type, filename in configs:
        output_df = clean_and_split(df, src_col, event_type)
        output_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Successfully generated: {filename} ({len(output_df)} entries)")

if __name__ == "__main__":
    process_market_data('data.xlsx')
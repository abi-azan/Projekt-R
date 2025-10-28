import os
import openpyxl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


EXCEL_FILE = os.path.join(BASE_DIR, "data.xlsx")      
OUTPUT_FILE = os.path.join(BASE_DIR, "tickers.txt")   


wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
ws = wb["List1"]  # koristi List1

tickers = set()


def add_tickers_from_column(column_index, start_row=2, end_row=55):
    for row in range(start_row, end_row + 1):
        cell_value = ws.cell(row=row, column=column_index).value
        if not cell_value:
            continue
        parts = [t.strip().upper() for t in str(cell_value).split(";") if t.strip()]
        tickers.update(parts)


add_tickers_from_column(3)  
add_tickers_from_column(4)  


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for ticker in sorted(tickers):
        f.write(ticker + "\n")

print(f"Izdvojeno je {len(tickers)} tickera.")
print(f"Spremljeno u datoteku: {OUTPUT_FILE}")

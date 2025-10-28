import os
import pandas as pd

input_dir = 'c:\\ferprogrami\\.vscode\\PROJEKT R\\downloaded_xlsx'
output_excel = 'sve_dionice_merged.xlsx'

xlsx_fajlovi = [f for f in os.listdir(input_dir) if f.endswith('.xlsx')]
if not xlsx_fajlovi:
    raise Exception("Nema .xlsx datoteka u folderu!")

with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    sheet_unesen = False
    for xlsx_file in xlsx_fajlovi:
        path = os.path.join(input_dir, xlsx_file)
        ticker = xlsx_file.split('_')[0]
        sheet_name = ticker[:31]
        try:
            df = pd.read_excel(path)
            if not df.empty:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                sheet_unesen = True
        except Exception as e:
            print(f"Preskačem {xlsx_file} zbog greške: {e}")

    if not sheet_unesen:
        raise Exception("Niti jedan sheet nije kreiran – provjeri ulazne fajlove!")

print("Sve spojeno, svaki sheet je ticker.")

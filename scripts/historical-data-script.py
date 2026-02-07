import os
import requests

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

input_file = 'data/txt/ticker-isin.txt'
output_dir = 'data/raw/downloaded_xlsx'
start_date = '2010-01-01'
end_date = '2025-10-27'

os.makedirs(output_dir, exist_ok=True)

with open(input_file, 'r') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        ticker, isin = line.split(",")
        url = f'https://rest.zse.hr/web/Bvt9fe2peQ7pwpyYqODM/security-history/XZAG/{isin}/{start_date}/{end_date}/xlsx'
        xlsx_path = os.path.join(output_dir, f'{ticker}_{isin}.xlsx')
        print(f'Dohvaćam {ticker} ({isin}) ...')
        resp = requests.get(url)
        with open(xlsx_path, 'wb') as outf:
            outf.write(resp.content)

import requests, re, csv
from bs4 import BeautifulSoup
from datetime import datetime

with open("linkovi.txt", "r", encoding="utf-8") as f:
    links = [line.strip() for line in f if line.strip()]

def extract_date(text):
    match = re.search(r"\b(\d{2}\.\d{2}\.\d{4}\.)", text)
    if match:
        return datetime.strptime(match.group(1), "%d.%m.%Y.").strftime("%Y-%m-%d")
    return None

def extract_implementation_date(text):
    patterns = [
        r"počevši od\s+(\d{1,2}\.\s*\w+\s*\d{4})",
        r"nakon završetka trgovine\s+dana\s+(\d{1,2}\.\s*\w+\s*\d{4})",
        r"nakon završetka trgovine\s+(\d{1,2}\.\s*\w+\s*\d{4})",  
        r"U indeksu CROBEX® od\s+(\d{1,2}\.\s*\w+\s*\d{4})"
    ]
    mjeseci = {
        'siječnja': 1, 'veljače': 2, 'ožujka': 3, 'travnja': 4,
        'svibnja': 5, 'lipnja': 6, 'srpnja': 7, 'kolovoza': 8,
        'rujna': 9, 'listopada': 10, 'studenoga': 11, 'prosinaca': 12
    }
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            parts = re.match(r"(\d{1,2})\.\s*(\w+)\s*(\d{4})", date_str)
            if parts:
                dan = int(parts.group(1))
                mjesec_hr = parts.group(2).lower()
                godina = int(parts.group(3))
                mjesec = mjeseci.get(mjesec_hr)
                if mjesec:
                    datum = datetime(godina, mjesec, dan)
                    return datum.strftime("%Y-%m-%d")
    return "N/A"


rows = []

for url in links:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        datum = extract_date(text)
        datum_provedbe = extract_implementation_date(text)
        tip = 'izvanredna' if 'izvanredna' in url.lower() else 'redovna'

        rows.append({
            'datum_objave_revizije': datum,
            'tip': tip,
            'datum_provedbe_revizije': datum_provedbe,
            'url': url
        })

    except Exception as e:
        rows.append({
            'datum_objave_revizije': None,
            'tip': None,
            'datum_provedbe_revizije': None,
            'url': url
        })

with open('revizije_tip.csv', 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['datum_objave_revizije', 'tip', 'datum_provedbe_revizije', 'url'])
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

print("Gotovo, podaci su spremljeni u 'revizije_tip.csv'")

# Projekt R

Repozitorij sadrži projekt izrađen u sklopu kolegija **Projekt R** pod mentorstvom doc. dr. sc. Stjepana Begušića na Fakultetu elektrotehnike i računarstva.

## Opis projekta

Analiza učinaka rebalansiranja indeksa CROBEX na cijene dionica. Projekt ispituje abnormalne prinose (AR/CAR) oko datuma uključivanja i isključivanja dionica iz indeksa te gradi portfeljske strategije temeljene na tim događajima.

## Struktura repozitorija

```
.
├── analysis/                 # Analitičke skripte (portfelji, CAR, t-testovi)
│   ├── abnormal_return_analysis_t-test.py
│   ├── car-testing.py
│   ├── long_short_portfolio.py
│   ├── portfolio_analysis_rebalanced.py
│   ├── portfolio_analysis_v3.py
│   ├── portfolio_graph_v2.py
│   └── Jupiter.ipynb
│
├── scripts/                  # Pomoćne skripte za obradu podataka
│   ├── A_HRK_EURconv.py          # HRK → EUR konverzija
│   ├── B_dodavanjeiMicanjeRedaka.py  # Popunjavanje vremenskog niza
│   ├── C_sinkronizacija.py       # Pivot tablice i grafovi po tickeru
│   ├── data_separator.py         # Razdvajanje redovnih/izvanrednih događaja
│   ├── deletions.py / insertions.py  # Generiranje event CSV-ova
│   ├── historical-data-script.py # Preuzimanje podataka sa ZSE API-ja
│   ├── xlsx-merge.py             # Spajanje XLSX datoteka
│   └── ...
│
├── data/
│   ├── raw/                  # Neobrađeni podaci
│   │   └── stocks_raw_data/  # Pojedinačni XLSX-ovi sa ZSE-a
│   ├── processed/            # Obrađeni podaci
│   │   └── sve_dionice_merged_EUR_filled.xlsx
│   ├── events/               # Event signali (datumi uključivanja/isključivanja)
│   └── txt/                  # Referentne datoteke (tickeri, ISIN-ovi)
│
├── outputs/
│   ├── csv/                  # Rezultati analiza u CSV formatu
│   ├── plots/                # Vizualizacije
│   │   └── plots_by_ticker/  # Grafovi po pojedinoj dionici
│   ├── car_testing/          # CAR rezultati
│   └── reports/              # Izvještaji
│
├── docs/                     # Dokumentacija i prezentacije
├── paper.tex                 # Istraživački rad (LaTeX)
└── SCRIPTS.md                # Detaljna dokumentacija svih skripti
```

## Pokretanje

### Preduvjeti

```
pip install pandas openpyxl xlsxwriter matplotlib numpy scipy statsmodels requests
```

### Pipeline za obradu podataka

1. **Preuzimanje podataka**: `python scripts/historical-data-script.py`
2. **Spajanje u jednu datoteku**: `python scripts/xlsx-merge.py`
3. **HRK → EUR konverzija**: `python scripts/A_HRK_EURconv.py`
4. **Popunjavanje vremenskog niza**: `python scripts/B_dodavanjeiMicanjeRedaka.py`
5. **Generiranje event signala**: `python scripts/data_separator.py`

### Analiza

```bash
python analysis/abnormal_return_analysis_t-test.py   # Abnormalni prinosi + t-test
python analysis/car-testing.py                        # CAR oko efektivnog datuma
python analysis/long_short_portfolio.py               # Long/short portfelj
python analysis/portfolio_analysis_rebalanced.py      # R-style rebalansirani portfelj
```

Sve skripte automatski pronalaze projektni root direktorij, pa se mogu pokrenuti iz bilo kojeg direktorija.

## Detaljni opis skripti

Pogledajte [SCRIPTS.md](SCRIPTS.md) za potpuni pregled svih skripti s ulazima, izlazima i napomenama.

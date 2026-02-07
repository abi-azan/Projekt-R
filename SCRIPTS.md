# Script Guide

This document summarizes what each Python script does, with inputs, outputs, and notes for future use.

All scripts auto-detect the project root via `os.chdir`, so they can be run from any directory:
```
python analysis/long_short_portfolio.py
python scripts/A_HRK_EURconv.py
```

## Common datasets
- `data/raw/data.xlsx`: CROBEX revisions table (announcement date, effective date, added/removed tickers).
- `data/events/INSERTIONS_ANN_EVENT.csv` / `data/events/DELETIONS_ANN_EVENT.csv`: stock-level event signals (announcement + effective dates).
- `data/events/regular_added.csv`, `data/events/irregular_added.csv`, `data/events/regular_deleted.csv`, `data/events/irregular_deleted.csv`: regular/extraordinary splits.
- `data/processed/sve_dionice_merged.xlsx`: merged per-ticker price history (one sheet per ticker).
- `data/processed/sve_dionice_merged_EUR.xlsx`: HRK to EUR converted version.
- `data/processed/sve_dionice_merged_EUR_filled.xlsx`: filled daily timeline with zero volumes and forward-filled prices.

## analysis/ scripts

- `analysis/abnormal_return_analysis_t-test.py`
  - Purpose: Computes daily equal-weight portfolio returns in the announcement-to-effective window, abnormal returns vs CROBEX, and a t-test.
  - Inputs: `data/events/INSERTIONS_ANN_EVENT.csv`, `data/events/DELETIONS_ANN_EVENT.csv`, `data/processed/sve_dionice_merged_EUR_filled.xlsx` (CBX sheet).
  - Outputs: `outputs/csv/insertions_abnormal_returns_daily.csv`, `outputs/csv/deletions_abnormal_returns_daily.csv`, console stats table.

- `analysis/car-testing.py`
  - Purpose: Builds a +/- window around the effective date and computes AR/CAR using Last Price returns.
  - Inputs: `data/events/INSERTIONS_EVENT.csv` or `data/events/DELETIONS_EVENT.csv`, `data/processed/sve_dionice_merged_EUR_filled.xlsx`, `CBX` sheet.
  - Outputs: `outputs/car_testing/` (optional per-event CSVs, `CAR_prosjek.csv`, plot).
  - Notes: Skips DDJH deletion on 2022-07-14 as an outlier.

- `analysis/long_short_portfolio.py`
  - Purpose: Daily rebalanced long/short portfolio (long insertions, short deletions).
  - Inputs: `data/events/INSERTIONS_ANN_EVENT.csv`, `data/events/DELETIONS_ANN_EVENT.csv`, `data/processed/sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: `outputs/csv/long_short_portfolio_results.csv`, `outputs/plots/long_short_portfolio.png`.
  - Notes: Uses equal-weight daily returns between announcement and effective dates on each side.

- `analysis/portfolio_analysis_rebalanced.py`
  - Purpose: Daily rebalanced equal-weight event-window portfolio (R-style method), split into regular/extraordinary groups.
  - Inputs: `data/events/INSERTIONS_ANN_EVENT.csv`, `data/events/DELETIONS_ANN_EVENT.csv`, `data/events/regular_added.csv`, `data/events/irregular_added.csv`, `data/events/regular_deleted.csv`, `data/events/irregular_deleted.csv`, `data/processed/sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: `outputs/plots/r_style_analysis_output.png`, `outputs/plots/r_style_detailed_analysis_output.png`, `outputs/csv/r_style_insertions_results.csv`, `outputs/csv/r_style_deletions_results.csv`.

- `analysis/portfolio_analysis_v3.py`
  - Purpose: Event-trading portfolio with equal capital split per announcement date, held until effective date.
  - Inputs: `data/events/INSERTIONS_ANN_EVENT.csv`, `data/events/DELETIONS_ANN_EVENT.csv`, `data/processed/sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: `outputs/csv/insertions_portfolio_results.csv`, `outputs/csv/deletions_portfolio_results.csv`, `outputs/plots/portfolio_comparison.png`.
  - Notes: Uses `Change Prev Close Percentage` for compounding.

- `analysis/portfolio_graph_v2.py`
  - Purpose: Sequential all-cash event-trading portfolio using Open Price for entry/exit.
  - Inputs: `data/events/INSERTIONS_ANN_EVENT.csv`, `data/events/DELETIONS_ANN_EVENT.csv`, `data/processed/sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: `outputs/csv/insertions_portfolio_results.csv`, `outputs/csv/deletions_portfolio_results.csv`, `outputs/plots/portfolio_comparison.png`.
  - Notes: Uses all cash per trade and does not overlap positions.

- `analysis/Jupiter.ipynb`
  - Purpose: Interactive notebook for data exploration and processing pipeline.
  - Notes: References may need manual updating to match new directory structure.

## scripts/ folder (data processing utilities)

### Data pipeline (run in order: A -> B -> C)

- `scripts/A_HRK_EURconv.py`
  - Purpose: Convert HRK prices/turnover in `sve_dionice_merged.xlsx` to EUR.
  - Inputs: `data/processed/sve_dionice_merged.xlsx`.
  - Outputs: `data/processed/sve_dionice_merged_EUR.xlsx`, console summary.

- `scripts/B_dodavanjeiMicanjeRedaka.py`
  - Purpose: Create a complete daily timeline per ticker, forward-fill prices/meta, zero out volumes/trades on inserted days, and remove BLOCK/OTC.
  - Inputs: `data/processed/sve_dionice_merged_EUR.xlsx`.
  - Outputs: `data/processed/sve_dionice_merged_EUR_filled.xlsx`.

- `scripts/C_sinkronizacija.py`
  - Purpose: Build a pivot table (date x ticker) for a selected metric and plot each ticker.
  - Inputs: `data/processed/sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: `outputs/plots/plots_by_ticker/` (one PNG per ticker), optional pivot CSV/XLSX.
  - Notes: Adjust `metric` and aggregation at the top of the script.

### Event data generation

- `scripts/data_separator.py`
  - Purpose: Splits `data.xlsx` into regular/extraordinary insertions/deletions CSVs.
  - Inputs: `data/raw/data.xlsx` (columns in Croatian: `redovna / izvanredna`, `Uključeni`, `Isključeni`).
  - Outputs: `data/events/regular_added.csv`, `data/events/irregular_added.csv`, `data/events/regular_deleted.csv`, `data/events/irregular_deleted.csv`.

- `scripts/deletions.py`
  - Purpose: Builds `DELETIONS_ANN_EVENT.csv` from `data.xlsx` (column C for deleted tickers).
  - Inputs: `data/raw/data.xlsx` (AnnDate in col A, EventDate in col E, tickers in col C).
  - Outputs: `data/events/DELETIONS_ANN_EVENT.csv`.

- `scripts/insertions.py`
  - Purpose: Builds `INSERTIONS_ANN_EVENT.csv` from `data.xlsx` (column D for added tickers).
  - Inputs: `data/raw/data.xlsx` (AnnDate in col A, EventDate in col E, tickers in col D).
  - Outputs: `data/events/INSERTIONS_ANN_EVENT.csv`.

### Stock data acquisition

- `scripts/historical-data-script.py`
  - Purpose: Download historical stock data from ZSE REST API.
  - Inputs: `data/txt/ticker-isin.txt`.
  - Outputs: `data/raw/downloaded_xlsx/` (one file per ticker+ISIN).
  - Notes: Requires network access and the `requests` package.

- `scripts/xlsx-merge.py`
  - Purpose: Merge downloaded per-ticker XLSX files into a single workbook (one sheet per ticker).
  - Inputs: `data/raw/downloaded_xlsx/`.
  - Outputs: `data/processed/sve_dionice_merged.xlsx`.

- `scripts/ticker-xlsx-extract.py`
  - Purpose: Extract unique tickers from `data.xlsx`.
  - Inputs: `data/raw/data.xlsx` (sheet `List1`, columns C and D).
  - Outputs: `data/txt/tickers.txt`.

### CAR event study

- `scripts/CAR_analysis.py`
  - Purpose: Market-model event study (AAR/CAAR) using per-ticker CSV files.
  - Inputs: `data/raw/inserted-deleted.xlsx`, market index CSV, per-ticker CSVs.
  - Outputs: CAAR plots in `outputs/plots/`.
  - Notes: Uses `statsmodels` and log returns.

- `scripts/CAR_working_one_event.py`
  - Purpose: Market-model event study (AAR/CAAR) using `sve_dionice_merged_EUR_filled.xlsx` sheets.
  - Inputs: `data/raw/inserted-deleted.xlsx`, market index CSV, `data/processed/sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: CAAR plots.
  - Notes: Uses `statsmodels` and log returns; loads all sheets into memory.

### Web scraping utilities

- `scripts/automatic-link-getter.py`
  - Purpose: Scrape ZSE index news page to collect revision links.
  - Inputs: ZSE website (network).
  - Outputs: `file.txt` (raw links).

- `scripts/link-parser.py`
  - Purpose: Extract href links from a saved HTML file.
  - Inputs: `ulaz.txt` (HTML).
  - Outputs: `linkovi.txt` with full ZSE URLs.

- `scripts/web-data-extract.py`
  - Purpose: Parse ZSE revision pages to extract announcement and implementation dates.
  - Inputs: `linkovi.txt` (URLs), ZSE website (network).
  - Outputs: `revizije_tip.csv`.

### Debugging helpers

- `scripts/return_stock_price_on_date.py`
  - Purpose: Helper to fetch stock and index prices on or after event dates.
  - Inputs: `data/raw/inserted-deleted.xlsx`, market index CSV, `data/processed/sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: Console output (debugging utility).

# Script Guide

This document summarizes what each Python script does, with inputs, outputs, and notes for future use.

## Common datasets
- `data.xlsx`: CROBEX revisions table (announcement date, effective date, added/removed tickers).
- `INSERTIONS_ANN_EVENT.csv` / `DELETIONS_ANN_EVENT.csv`: stock-level event signals (announcement + effective dates).
- `regular_added.csv`, `irregular_added.csv`, `regular_deleted.csv`, `irregular_deleted.csv`: regular/extraordinary splits (file names still say irregular).
- `sve_dionice_merged.xlsx`: merged per-ticker price history (one sheet per ticker).
- `sve_dionice_merged_EUR.xlsx`: HRK to EUR converted version.
- `sve_dionice_merged_EUR_filled.xlsx`: filled daily timeline with zero volumes and forward-filled prices.

## Root-level scripts
- `abnormal_return_analasys_t-test.py`
  - Purpose: Computes daily equal-weight portfolio returns in the announcement-to-effective window, abnormal returns vs CROBEX, and a t-test.
  - Inputs: `INSERTIONS_ANN_EVENT.csv`, `DELETIONS_ANN_EVENT.csv`, `sve_dionice_merged_EUR_filled.xlsx` (CBX sheet).
  - Outputs: `insertions_abnormal_returns_daily.csv`, `deletions_abnormal_returns_daily.csv`, console stats table.

- `car-testing.py`
  - Purpose: Builds a +/- window around the effective date and computes AR/CAR using Last Price returns.
  - Inputs: `INSERTIONS_EVENT.csv` or `DELETIONS_EVENT.csv`, `sve_dionice_merged_EUR_filled.xlsx`, `CBX` sheet.
  - Outputs: `testiranje_car_skripta/` (optional per-event CSVs, `CAR_prosjek.csv`, plot).
  - Notes: Skips DDJH deletion on 2022-07-14 as an outlier.

- `data-seperator.py`
  - Purpose: Splits `data.xlsx` into regular/extraordinary insertions/deletions CSVs.
  - Inputs: `data.xlsx` (columns in Croatian: `redovna / izvanredna`, `Uključeni`, `Isključeni`).
  - Outputs: `regular_added.csv`, `irregular_added.csv`, `regular_deleted.csv`, `irregular_deleted.csv`.

- `deletions.py`
  - Purpose: Builds `DELETIONS_ANN_EVENT.csv` from `data.xlsx` (column C for deleted tickers).
  - Inputs: `data.xlsx` (AnnDate in col A, EventDate in col E, tickers in col C).
  - Outputs: `DELETIONS_ANN_EVENT.csv`.

- `insertions.py`
  - Purpose: Builds `INSERTIONS_ANN_EVENT.csv` from `data.xlsx` (column D for added tickers).
  - Inputs: `data.xlsx` (AnnDate in col A, EventDate in col E, tickers in col D).
  - Outputs: `INSERTIONS_ANN_EVENT.csv`.

- `portfolio_analasys_v3.py`
  - Purpose: Event-trading portfolio with equal capital split per announcement date, held until effective date.
  - Inputs: `INSERTIONS_ANN_EVENT.csv`, `DELETIONS_ANN_EVENT.csv`, `sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: `insertions_portfolio_results.csv`, `deletions_portfolio_results.csv`, `portfolio_comparison.png`.
  - Notes: Uses `Change Prev Close Percentage` for compounding.

- `portfolio_analasys_rebalanced.py`
  - Purpose: Daily rebalanced equal-weight event-window portfolio (R-style method), split into regular/extraordinary groups.
  - Inputs: `INSERTIONS_ANN_EVENT.csv`, `DELETIONS_ANN_EVENT.csv`, `regular_added.csv`, `irregular_added.csv`, `regular_deleted.csv`, `irregular_deleted.csv`, `sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: `r_style_analysis_output.png`, `r_style_detailed_analysis_output.png`, `r_style_insertions_results.csv`, `r_style_deletions_results.csv`.

- `portfolio_graph_v2.py`
  - Purpose: Sequential all-cash event-trading portfolio using Open Price for entry/exit.
  - Inputs: `INSERTIONS_ANN_EVENT.csv`, `DELETIONS_ANN_EVENT.csv`, `sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: `insertions_portfolio_results.csv`, `deletions_portfolio_results.csv`, `portfolio_comparison.png`.
  - Notes: Uses all cash per trade and does not overlap positions.

- `long_short_portfolio.py`
  - Purpose: Daily rebalanced long/short portfolio (long insertions, short deletions).
  - Inputs: `INSERTIONS_ANN_EVENT.csv`, `DELETIONS_ANN_EVENT.csv`, `sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: `long_short_portfolio_results.csv`, `long_short_portfolio.png`.
  - Notes: Uses equal-weight daily returns between announcement and effective dates on each side.

## scripts/ folder
- `scripts/historical-data-script.py`
  - Purpose: Download historical stock data from ZSE REST API.
  - Inputs: `txt/ticker-isin.txt`.
  - Outputs: `downloaded_xlsx/` (one file per ticker+ISIN).
  - Notes: Requires network access and the `requests` package.

- `scripts/A_HRK_EURconv.py`
  - Purpose: Convert HRK prices/turnover in `sve_dionice_merged.xlsx` to EUR.
  - Inputs: `sve_dionice_merged.xlsx`.
  - Outputs: `sve_dionice_merged_EUR.xlsx`, console summary.

- `scripts/B_dodavanjeiMicanjeRedaka.py`
  - Purpose: Create a complete daily timeline per ticker, forward-fill prices/meta, zero out volumes/trades on inserted days, and remove BLOCK/OTC.
  - Inputs: `sve_dionice_merged_EUR.xlsx`.
  - Outputs: `sve_dionice_merged_EUR_filled.xlsx`.

- `scripts/C_sinkronizacija.py`
  - Purpose: Build a pivot table (date x ticker) for a selected metric and plot each ticker.
  - Inputs: `sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: `plots_by_ticker/` (one PNG per ticker), optional pivot CSV/XLSX.
  - Notes: Adjust `metric` and aggregation at the top of the script.

- `scripts/CAR_analysys.py`
  - Purpose: Market-model event study (AAR/CAAR) using per-ticker CSV files.
  - Inputs: `xlsx/inserted-deleted.xlsx`, market index CSV, per-ticker CSVs named like `sve_dionice_merged_EUR_filled.xlsx - TICKER.csv`.
  - Outputs: CAAR plots for insertions/deletions.
  - Notes: Uses `statsmodels` and log returns.

- `scripts/CAR_working_one_event.py`
  - Purpose: Market-model event study (AAR/CAAR) using `sve_dionice_merged_EUR_filled.xlsx` sheets.
  - Inputs: `xlsx/inserted-deleted.xlsx`, market index CSV, `sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: CAAR plots for insertions/deletions.
  - Notes: Uses `statsmodels` and log returns; loads all sheets into memory.

- `scripts/automatic-link-getter.py`
  - Purpose: Scrape ZSE index news page to collect revision links.
  - Inputs: ZSE website (network).
  - Outputs: `file.txt` (raw links).
  - Notes: Script looks incomplete (reads `links.txt` but writes `file.txt`).

- `scripts/link-parser.py`
  - Purpose: Extract href links from a saved HTML file.
  - Inputs: `ulaz.txt` (HTML).
  - Outputs: `linkovi.txt` with full ZSE URLs.

- `scripts/web-data-extract.py`
  - Purpose: Parse ZSE revision pages to extract announcement and implementation dates.
  - Inputs: `linkovi.txt` (URLs), ZSE website (network).
  - Outputs: `revizije_tip.csv`.

- `scripts/ticker-xlsx-extract.py`
  - Purpose: Extract unique tickers from `data.xlsx`.
  - Inputs: `data.xlsx` (sheet `List1`, columns C and D).
  - Outputs: `tickers.txt`.

- `scripts/return_stock_price_on_date.py`
  - Purpose: Helper to fetch stock and index prices on or after event dates.
  - Inputs: `xlsx/inserted-deleted.xlsx`, market index CSV, `sve_dionice_merged_EUR_filled.xlsx`.
  - Outputs: Prints a sample lookup result (debugging utility).

- `scripts/xlsx-merge.py`
  - Purpose: Merge downloaded per-ticker XLSX files into a single workbook (one sheet per ticker).
  - Inputs: `downloaded_xlsx/` (path is hardcoded in script).
  - Outputs: `sve_dionice_merged.xlsx`.
  - Notes: Update `input_dir` to match your local path.

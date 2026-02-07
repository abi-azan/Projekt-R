import pandas as pd
import matplotlib.pyplot as plt
import os

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def build_daily_returns(signals_path, excel_reader, master_dates, ret_col="Change Prev Close Percentage"):
    """
    Build equal-weight daily returns for all stocks active between AnnDate and EventDate.
    """
    signals = pd.read_csv(signals_path)
    signals["AnnDate"] = pd.to_datetime(signals["AnnDate"])
    signals["EventDate"] = pd.to_datetime(signals["EventDate"])

    all_active_data = []

    for _, row in signals.iterrows():
        ticker = row["Symbol"]
        if ticker not in excel_reader.sheet_names:
            continue

        df = pd.read_excel(excel_reader, sheet_name=ticker)
        df["Date"] = pd.to_datetime(df["Date"])

        mask = (df["Date"] >= row["AnnDate"]) & (df["Date"] <= row["EventDate"])
        active_segment = df.loc[mask, ["Date", ret_col]].copy()

        if not active_segment.empty:
            all_active_data.append(active_segment)

    if not all_active_data:
        portfolio = pd.DataFrame(index=master_dates).sort_index()
        portfolio["daily_ret"] = 0.0
        return portfolio.reset_index().rename(columns={"index": "Date"})

    window_df = pd.concat(all_active_data)
    window_df[ret_col] = window_df[ret_col].fillna(0)

    counts = window_df.groupby("Date").size().rename("count")
    window_df = window_df.join(counts, on="Date")
    window_df["adjusted_return"] = window_df[ret_col] / window_df["count"]

    daily_portfolio_returns = window_df.groupby("Date")["adjusted_return"].sum().rename("daily_ret")

    portfolio = pd.DataFrame(index=master_dates).sort_index()
    portfolio = portfolio.join(daily_portfolio_returns, how="left")
    portfolio["daily_ret"] = portfolio["daily_ret"].fillna(0)

    return portfolio.reset_index().rename(columns={"index": "Date"})


# --- MAIN EXECUTION ---

excel_file = "data/processed/sve_dionice_merged_EUR_filled.xlsx"
reader = pd.ExcelFile(excel_file)

# Master timeline from CROBEX (CBX)
cbx_df = pd.read_excel(reader, sheet_name="CBX")
master_dates = pd.to_datetime(cbx_df["Date"]).unique()

# Long insertions, short deletions
long_df = build_daily_returns("data/events/INSERTIONS_ANN_EVENT.csv", reader, master_dates)
short_df = build_daily_returns("data/events/DELETIONS_ANN_EVENT.csv", reader, master_dates)

merged = long_df.merge(short_df, on="Date", how="inner", suffixes=("_long", "_short"))
merged["ls_ret"] = merged["daily_ret_long"] - merged["daily_ret_short"]

# Portfolio value (base 1.0)
merged["Value"] = (1 + merged["ls_ret"]).cumprod()
merged["Return_Pct"] = (merged["Value"] - 1) * 100

merged.to_csv("outputs/csv/long_short_portfolio_results.csv", index=False)

# Plot
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

axes[0].plot(merged["Date"], merged["Value"], color="black", linewidth=2)
axes[0].axhline(y=1.0, color="red", linestyle="--", alpha=0.6)
axes[0].set_title("Long Insertions / Short Deletions (Daily Rebalanced)", fontsize=14)
axes[0].set_ylabel("Portfolio Value (Base 1.0)")
axes[0].grid(True, alpha=0.3)

axes[1].plot(merged["Date"], merged["Return_Pct"], color="blue", linewidth=2)
axes[1].axhline(y=0, color="red", linestyle="--", alpha=0.6)
axes[1].set_xlabel("Date")
axes[1].set_ylabel("Cumulative Return (%)")
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/plots/long_short_portfolio.png", dpi=300)

final_value = merged["Value"].iloc[-1]
final_return = merged["Return_Pct"].iloc[-1]
print(f"Final Value: {final_value:.4f}")
print(f"Total Return: {final_return:.2f}%")

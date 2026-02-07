import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def process_r_style_portfolio(signals_path, excel_reader, master_dates):
    """
    Calculates portfolio performance using the R script method:
    1. Aggregates all active stock windows.
    2. Calculates an equally weighted average return for each day.
    3. Compounds the daily aggregate returns.
    """
    # 1. Load trading signals (Insertions or Deletions)
    signals = pd.read_csv(signals_path)
    signals['AnnDate'] = pd.to_datetime(signals['AnnDate'])
    signals['EventDate'] = pd.to_datetime(signals['EventDate'])
    
    all_active_data = []
    
    # 2. Extract active windows (between AnnDate and EventDate)
    for _, row in signals.iterrows():
        ticker = row['Symbol']
        if ticker in excel_reader.sheet_names:
            df = pd.read_excel(excel_reader, sheet_name=ticker)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Filter the 'window' as done in R
            mask = (df['Date'] >= row['AnnDate']) & (df['Date'] <= row['EventDate'])
            active_segment = df.loc[mask].copy()
            
            if not active_segment.empty:
                all_active_data.append(active_segment)
    
    if not all_active_data:
        return pd.DataFrame()

    # Combine all segments into one "Long" dataframe
    window_df = pd.concat(all_active_data)
    
    # 3. Handle Missing Values
    # R: window_insertion$`Change Prev Close Percentage`[is.na(...)] <- 0
    ret_col = 'Change Prev Close Percentage'
    window_df[ret_col] = window_df[ret_col].fillna(0)
    
    # 4. Calculate Daily Weights (R: add_count(Date))
    # Count how many stocks are active on each specific date
    counts = window_df.groupby('Date').size().rename('count')
    window_df = window_df.join(counts, on='Date')
    
    # 5. Calculate Adjusted Daily Returns
    # R: adjusted_return = return / count
    # This ensures that if 5 stocks are active, each contributes 1/5th to the daily return.
    window_df['adjusted_return'] = window_df[ret_col] / window_df['count']
    
    # 6. Aggregate Daily Portfolio Return
    # R: summarise(portfolio_return = sum(adjusted_return))
    daily_portfolio_returns = window_df.groupby('Date')['adjusted_return'].sum().rename('daily_ret')
    
    # 7. Merge with Master Timeline (R: left_join(df_dates))
    portfolio = pd.DataFrame(index=master_dates).sort_index()
    portfolio = portfolio.join(daily_portfolio_returns, how='left')
    portfolio['daily_ret'] = portfolio['daily_ret'].fillna(0)
    
    # 8. Cumulative Compounding
    # R: value = cumprod(1 + portfolio_return)
    portfolio['Value'] = (1 + portfolio['daily_ret']).cumprod()
    portfolio['Return_Pct'] = (portfolio['Value'] - 1) * 100
    
    return portfolio.reset_index().rename(columns={'index': 'Date'})

# --- MAIN EXECUTION ---

# Load Excel data
excel_file = 'data/processed/sve_dionice_merged_EUR_filled.xlsx'
reader = pd.ExcelFile(excel_file)

# Get the master timeline from CROBEX (CBX) as the R script does
cbx_df = pd.read_excel(reader, sheet_name='CBX')
master_dates = pd.to_datetime(cbx_df['Date']).unique()

# Process both portfolios
insertions_portfolio = process_r_style_portfolio('data/events/INSERTIONS_ANN_EVENT.csv', reader, master_dates)
deletions_portfolio = process_r_style_portfolio('data/events/DELETIONS_ANN_EVENT.csv', reader, master_dates)
regular_insertions_portfolio = process_r_style_portfolio('data/events/regular_added.csv', reader, master_dates)
irregular_insertions_portfolio = process_r_style_portfolio('data/events/irregular_added.csv', reader, master_dates)
regular_deletions_portfolio = process_r_style_portfolio('data/events/regular_deleted.csv', reader, master_dates)
irregular_deletions_portfolio = process_r_style_portfolio('data/events/irregular_deleted.csv', reader, master_dates)
# --- GRAPH DRAWING ---

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Plot Insertions
ax1.plot(insertions_portfolio['Date'], insertions_portfolio['Value'], color='blue', label='Insertions Portfolio')
ax1.axhline(y=1.0, color='red', linestyle='--', alpha=0.6)
ax1.set_title('Insertions Portfolio Performance (R-Method: Daily Rebalanced)', fontsize=14)
ax1.set_ylabel('Portfolio Value (Base 1.0)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot Deletions
ax2.plot(deletions_portfolio['Date'], deletions_portfolio['Value'], color='orange', label='Deletions Portfolio')
ax2.axhline(y=1.0, color='red', linestyle='--', alpha=0.6)
ax2.set_title('Deletions Portfolio Performance (R-Method: Daily Rebalanced)', fontsize=14)
ax2.set_ylabel('Portfolio Value (Base 1.0)')
ax2.set_xlabel('Date')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/plots/r_style_analysis_output.png', dpi=300)

#Make a 2x2 layout for the regular and irregular insertions and deletions
fig, axes = plt.subplots(2, 2, figsize=(16, 12), sharex=True)
# Regular Insertions   
axes[0, 0].plot(regular_insertions_portfolio['Date'], regular_insertions_portfolio['Value'], color='green', label='Regular Insertions')
axes[0, 0].axhline(y=1.0, color='red', linestyle='--', alpha=0.6)
axes[0, 0].set_title('Regular Insertions Portfolio Performance', fontsize=14)
axes[0, 0].set_ylabel('Portfolio Value (Base 1.0)')     
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)
# Irregular Insertions
axes[0, 1].plot(irregular_insertions_portfolio['Date'], irregular_insertions_portfolio['Value'], color='purple', label='Irregular Insertions')
axes[0, 1].axhline(y=1.0, color='red', linestyle='--', alpha=0.6)
axes[0, 1].set_title('Irregular Insertions Portfolio Performance', fontsize=14)
axes[0, 1].set_ylabel('Portfolio Value (Base 1.0)')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)
# Regular Deletions
axes[1, 0].plot(regular_deletions_portfolio['Date'], regular_deletions_portfolio['Value'], color='brown', label='Regular Deletions')
axes[1, 0].axhline(y=1.0, color='red', linestyle='--', alpha=0.6)
axes[1, 0].set_title('Regular Deletions Portfolio Performance', fontsize=14)
axes[1, 0].set_ylabel('Portfolio Value (Base 1.0)')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)
# Irregular Deletions
axes[1, 1].plot(irregular_deletions_portfolio['Date'], irregular_deletions_portfolio['Value'], color='cyan', label='Irregular Deletions')
axes[1, 1].axhline(y=1.0, color='red', linestyle='--', alpha=0.6)
axes[1, 1].set_title('Irregular Deletions Portfolio Performance', fontsize=14)
axes[1, 1].set_ylabel('Portfolio Value (Base 1.0)') 
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/plots/r_style_detailed_analysis_output.png', dpi=300)

# Save results
insertions_portfolio.to_csv('outputs/csv/r_style_insertions_results.csv', index=False)
deletions_portfolio.to_csv('outputs/csv/r_style_deletions_results.csv', index=False)

print("Analysis complete. Graphs saved to 'r_style_analysis_output.png'.")
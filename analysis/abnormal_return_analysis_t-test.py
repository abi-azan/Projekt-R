import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import os

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def get_portfolio_daily_returns(signals_path, excel_reader):
    """
    Calculates the Daily Portfolio Return using the R-script method:
    Equally weighted average of all stocks active on a specific date.
    """
    # 1. Load Signals
    signals = pd.read_csv(signals_path)
    signals['AnnDate'] = pd.to_datetime(signals['AnnDate'])
    signals['EventDate'] = pd.to_datetime(signals['EventDate'])
    
    all_active_data = []
    
    # 2. Extract active windows
    for _, row in signals.iterrows():
        ticker = row['Symbol']
        if ticker in excel_reader.sheet_names:
            df = pd.read_excel(excel_reader, sheet_name=ticker)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Filter window: Announcement to Event
            mask = (df['Date'] >= row['AnnDate']) & (df['Date'] <= row['EventDate'])
            active_segment = df.loc[mask].copy()
            
            if not active_segment.empty:
                all_active_data.append(active_segment)
    
    if not all_active_data:
        return pd.DataFrame(columns=['Date', 'Portfolio_Ret'])

    # 3. Combine and Calculate Weighted Returns
    window_df = pd.concat(all_active_data)
    
    # Fill NA returns with 0
    ret_col = 'Change Prev Close Percentage'
    window_df[ret_col] = window_df[ret_col].fillna(0)
    
    # Count active stocks per day
    counts = window_df.groupby('Date').size().rename('count')
    window_df = window_df.join(counts, on='Date')
    
    # Calculate contribution of each stock (Return / Count)
    window_df['adjusted_return'] = window_df[ret_col] / window_df['count']
    
    # Sum adjusted returns to get Daily Portfolio Return
    daily_portfolio_returns = window_df.groupby('Date')['adjusted_return'].sum().rename('Portfolio_Ret')
    
    # Convert from percentage (e.g., 1.5) to decimal (0.015) for calculations if needed, 
    # but input 'Change Prev Close Percentage' usually is 1.5 for 1.5%. 
    # We will keep it as Percentage for the T-test to match standard reporting.
    
    return daily_portfolio_returns.reset_index()

def analyze_abnormal_returns(portfolio_name, signals_file, excel_reader, cbx_df):
    """
    Calculates Abnormal Returns (Portfolio - Benchmark) and T-stats.
    """
    # Get Portfolio Daily Returns
    port_df = get_portfolio_daily_returns(signals_file, excel_reader)
    
    if port_df.empty:
        return None

    # Merge with CROBEX (Benchmark) on Date
    # CBX data is expected to have 'Date' and 'Change Prev Close Percentage'
    merged_df = pd.merge(port_df, cbx_df[['Date', 'Change Prev Close Percentage']], on='Date', how='inner')
    merged_df.rename(columns={'Change Prev Close Percentage': 'Benchmark_Ret'}, inplace=True)
    
    # Calculate Abnormal Return (AR)
    # AR = Portfolio Return - Benchmark Return
    merged_df['Abnormal_Ret'] = merged_df['Portfolio_Ret'] - merged_df['Benchmark_Ret']
    
    # --- Statistical Analysis (T-Test) ---
    # Null Hypothesis: Mean Abnormal Return is 0
    t_stat, p_value = stats.ttest_1samp(merged_df['Abnormal_Ret'], 0)
    
    # Calculate stats
    n_obs = len(merged_df)
    mean_ar = merged_df['Abnormal_Ret'].mean()
    std_ar = merged_df['Abnormal_Ret'].std()
    mean_port = merged_df['Portfolio_Ret'].mean()
    mean_bench = merged_df['Benchmark_Ret'].mean()
    
    return {
        'Portfolio': portfolio_name,
        'N_Days': n_obs,
        'Mean_Portfolio_Daily_%': mean_port,
        'Mean_Benchmark_Daily_%': mean_bench,
        'Mean_Abnormal_Daily_%': mean_ar,
        'Std_Dev_AR': std_ar,
        'T_Statistic': t_stat,
        'P_Value': p_value
    }, merged_df

# --- MAIN EXECUTION ---

# 1. Load Data
excel_file = 'data/processed/sve_dionice_merged_EUR_filled.xlsx'
print("Loading Excel file...")
xls = pd.ExcelFile(excel_file)

# 2. Prepare Benchmark (CROBEX)
# "First sheet (CBX)"
cbx_df = pd.read_excel(xls, sheet_name='CBX')
cbx_df['Date'] = pd.to_datetime(cbx_df['Date'])
# Ensure return column exists (filling NA with 0)
cbx_df['Change Prev Close Percentage'] = cbx_df['Change Prev Close Percentage'].fillna(0)

# 3. Analyze Insertions
print("Analyzing Insertions...")
ins_stats, ins_data = analyze_abnormal_returns('INSERTIONS', 'data/events/INSERTIONS_ANN_EVENT.csv', xls, cbx_df)

# 4. Analyze Deletions
print("Analyzing Deletions...")
del_stats, del_data = analyze_abnormal_returns('DELETIONS', 'data/events/DELETIONS_ANN_EVENT.csv', xls, cbx_df)

# 5. Create Results Table
results_list = []
if ins_stats: results_list.append(ins_stats)
if del_stats: results_list.append(del_stats)

results_table = pd.DataFrame(results_list)

# Formatting the table for cleaner output
display_cols = ['Portfolio', 'N_Days', 'Mean_Abnormal_Daily_%', 'T_Statistic', 'P_Value']
final_view = results_table[display_cols].copy()

# Add significance stars
final_view['Significance'] = final_view['P_Value'].apply(lambda x: '***' if x < 0.01 else ('**' if x < 0.05 else ('*' if x < 0.1 else '')))

print("\n" + "="*60)
print("             DAILY ABNORMAL RETURNS ANALYSIS")
print("="*60)
print(final_view.to_string(index=False))
print("-" * 60)
print("Note: Mean_Abnormal_Daily_% is in percentage points.")
print("Significance: *** < 0.01, ** < 0.05, * < 0.1")

# 6. Save Detailed Time Series to CSV (Optional)
if ins_data is not None:
    ins_data.to_csv('outputs/csv/insertions_abnormal_returns_daily.csv', index=False)
if del_data is not None:
    del_data.to_csv('outputs/csv/deletions_abnormal_returns_daily.csv', index=False)
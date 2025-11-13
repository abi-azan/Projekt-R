import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

def process_portfolio(csv_file, excel_file, initial_capital=10000):
    """Process trades and return portfolio events"""
    # Read the CSV with trading signals
    trades_df = pd.read_csv(csv_file)
    print(f"\nLoaded {len(trades_df)} trades from {csv_file}")
    
    # Convert dates and sort by AnnDate to process chronologically
    trades_df['AnnDate'] = pd.to_datetime(trades_df['AnnDate'])
    trades_df['EventDate'] = pd.to_datetime(trades_df['EventDate'])
    trades_df = trades_df.sort_values('AnnDate').reset_index(drop=True)
    
    print(f"Date range: {trades_df['AnnDate'].min()} to {trades_df['EventDate'].max()}")
    
    # Store portfolio value over time
    portfolio_events = []
    cash = initial_capital
    positions = {}
    
    # Process each trade
    for idx, trade in trades_df.iterrows():
        symbol = trade['Symbol']
        ann_date = trade['AnnDate']
        event_date = trade['EventDate']
        
        # Check if sheet exists for this symbol
        if symbol not in excel_file.sheet_names:
            print(f"Warning: Sheet '{symbol}' not found in Excel file")
            continue
        
        # Read the stock data for this symbol
        stock_df = pd.read_excel(excel_file, sheet_name=symbol)
        stock_df['Date'] = pd.to_datetime(stock_df['Date'])
        stock_df = stock_df.sort_values('Date')
        
        # Find the buy price (Open Price on AnnDate)
        buy_data = stock_df[stock_df['Date'] == ann_date]
        if buy_data.empty:
            # If exact date not found, find nearest date
            buy_data = stock_df[stock_df['Date'] >= ann_date].head(1)
        
        if buy_data.empty:
            print(f"Warning: Could not find buy date for {symbol}")
            continue
        
        buy_price = buy_data.iloc[0]['Open Price']
        buy_date = buy_data.iloc[0]['Date']
        
        # Find the sell price (Open Price on EventDate)
        sell_data = stock_df[stock_df['Date'] == event_date]
        if sell_data.empty:
            # If exact date not found, find nearest date
            sell_data = stock_df[stock_df['Date'] >= event_date].head(1)
        
        if sell_data.empty:
            print(f"Warning: Could not find sell date for {symbol}")
            continue
        
        sell_price = sell_data.iloc[0]['Open Price']
        sell_date = sell_data.iloc[0]['Date']
        
        # Calculate shares bought (use all available cash)
        shares = np.floor(cash / buy_price)
        
        # Record buy
        portfolio_events.append({
            'Date': buy_date,
            'Symbol': symbol,
            'Action': 'BUY',
            'Price': buy_price,
            'Shares': shares,
            'Value': cash
        })
        
        # Calculate sell value
        sell_value = shares * sell_price
        cash = sell_value
        
        # Record sell
        portfolio_events.append({
            'Date': sell_date,
            'Symbol': symbol,
            'Action': 'SELL',
            'Price': sell_price,
            'Shares': shares,
            'Value': cash
        })
    
    return portfolio_events, cash

# Read the Excel file with all stock data
excel_file = pd.ExcelFile('sve_dionice_merged_EUR_filled.xlsx')
print(f"Found {len(excel_file.sheet_names)} sheets in Excel file")

initial_capital = 1000000  # Starting with 1,000,000 EUR

# Process INSERTIONS portfolio
insertions_events, insertions_final = process_portfolio('INSERTIONS_ANN_EVENT.csv', excel_file, initial_capital)

# Process DELETIONS portfolio
deletions_events, deletions_final = process_portfolio('DELETIONS_ANN_EVENT.csv', excel_file, initial_capital)

# Create the plots
fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# Process INSERTIONS
if insertions_events:
    portfolio_df = pd.DataFrame(insertions_events)
    portfolio_df = portfolio_df.sort_values('Date')
    portfolio_df['Return_Pct'] = ((portfolio_df['Value'] / initial_capital) - 1) * 100
    
    # INSERTIONS - Portfolio value
    axes[0, 0].plot(portfolio_df['Date'], portfolio_df['Value'], marker='o', linewidth=2, markersize=6, color='blue')
    axes[0, 0].axhline(y=initial_capital, color='r', linestyle='--', label='Initial Capital')
    axes[0, 0].set_xlabel('Date', fontsize=12)
    axes[0, 0].set_ylabel('Portfolio Value (EUR)', fontsize=12)
    axes[0, 0].set_title('INSERTIONS - Portfolio Value Over Time', fontsize=14, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # INSERTIONS - Cumulative returns
    axes[1, 0].plot(portfolio_df['Date'], portfolio_df['Return_Pct'], marker='o', 
             linewidth=2, markersize=6, color='green')
    axes[1, 0].axhline(y=0, color='r', linestyle='--', label='Break Even')
    axes[1, 0].set_xlabel('Date', fontsize=12)
    axes[1, 0].set_ylabel('Cumulative Return (%)', fontsize=12)
    axes[1, 0].set_title('INSERTIONS - Cumulative Returns Over Time', fontsize=14, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend()
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Save INSERTIONS results
    portfolio_df.to_csv('insertions_portfolio_results.csv', index=False)
    
    # Print INSERTIONS statistics
    total_return = ((insertions_final / initial_capital) - 1) * 100
    num_trades = len(insertions_events) // 2
    
    print("\n" + "="*50)
    print("INSERTIONS PORTFOLIO PERFORMANCE")
    print("="*50)
    print(f"Initial Capital:    {initial_capital:,.2f} EUR")
    print(f"Final Value:        {insertions_final:,.2f} EUR")
    print(f"Total Return:       {total_return:,.2f}%")
    print(f"Number of Trades:   {num_trades}")
    if num_trades > 0:
        print(f"Avg Return/Trade:   {total_return/num_trades:,.2f}%")
    print("="*50)

# Process DELETIONS
if deletions_events:
    portfolio_df = pd.DataFrame(deletions_events)
    portfolio_df = portfolio_df.sort_values('Date')
    portfolio_df['Return_Pct'] = ((portfolio_df['Value'] / initial_capital) - 1) * 100
    
    # DELETIONS - Portfolio value
    axes[0, 1].plot(portfolio_df['Date'], portfolio_df['Value'], marker='o', linewidth=2, markersize=6, color='purple')
    axes[0, 1].axhline(y=initial_capital, color='r', linestyle='--', label='Initial Capital')
    axes[0, 1].set_xlabel('Date', fontsize=12)
    axes[0, 1].set_ylabel('Portfolio Value (EUR)', fontsize=12)
    axes[0, 1].set_title('DELETIONS - Portfolio Value Over Time', fontsize=14, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # DELETIONS - Cumulative returns
    axes[1, 1].plot(portfolio_df['Date'], portfolio_df['Return_Pct'], marker='o', 
             linewidth=2, markersize=6, color='orange')
    axes[1, 1].axhline(y=0, color='r', linestyle='--', label='Break Even')
    axes[1, 1].set_xlabel('Date', fontsize=12)
    axes[1, 1].set_ylabel('Cumulative Return (%)', fontsize=12)
    axes[1, 1].set_title('DELETIONS - Cumulative Returns Over Time', fontsize=14, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend()
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    # Save DELETIONS results
    portfolio_df.to_csv('deletions_portfolio_results.csv', index=False)
    
    # Print DELETIONS statistics
    total_return = ((deletions_final / initial_capital) - 1) * 100
    num_trades = len(deletions_events) // 2
    
    print("\n" + "="*50)
    print("DELETIONS PORTFOLIO PERFORMANCE")
    print("="*50)
    print(f"Initial Capital:    {initial_capital:,.2f} EUR")
    print(f"Final Value:        {deletions_final:,.2f} EUR")
    print(f"Total Return:       {total_return:,.2f}%")
    print(f"Number of Trades:   {num_trades}")
    if num_trades > 0:
        print(f"Avg Return/Trade:   {total_return/num_trades:,.2f}%")
    print("="*50)

plt.tight_layout()
plt.savefig('portfolio_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nGraphs saved to 'portfolio_comparison.png'")
print("Detailed results saved to 'insertions_portfolio_results.csv' and 'deletions_portfolio_results.csv'")
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from collections import defaultdict

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
    
    # Group trades by buy date to split capital equally
    trades_by_date = defaultdict(list)
    for idx, trade in trades_df.iterrows():
        trades_by_date[trade['AnnDate']].append(trade)
    
    # Store portfolio value over time
    portfolio_timeline = []
    cash = initial_capital
    active_positions = {}  # {symbol: {'shares': X, 'buy_date': date, 'sell_date': date}}
    
    # Get all unique dates from trades
    all_dates = sorted(set(list(trades_df['AnnDate']) + list(trades_df['EventDate'])))
    
    # Process chronologically
    for current_date in all_dates:
        # Check for sells (positions closing)
        positions_to_close = []
        for symbol, position in active_positions.items():
            if position['sell_date'] == current_date:
                positions_to_close.append(symbol)
        
        # Close positions and calculate returns
        for symbol in positions_to_close:
            position = active_positions[symbol]
            
            # Read stock data
            stock_df = pd.read_excel(excel_file, sheet_name=symbol)
            stock_df['Date'] = pd.to_datetime(stock_df['Date'])
            stock_df = stock_df.sort_values('Date')
            
            # Get the percentage changes from buy date to sell date
            buy_data = stock_df[stock_df['Date'] == position['buy_date']]
            sell_data = stock_df[stock_df['Date'] == current_date]
            
            if sell_data.empty:
                sell_data = stock_df[stock_df['Date'] >= current_date].head(1)
            
            if not sell_data.empty:
                # Calculate cumulative return using "Change Prev Close Percentage"
                date_range = stock_df[(stock_df['Date'] > position['buy_date']) & 
                                     (stock_df['Date'] <= sell_data.iloc[0]['Date'])]
                
                if not date_range.empty and 'Change Prev Close Percentage' in date_range.columns:
                    # Cumulative return = product of (1 + daily_return) - 1
                    daily_returns = date_range['Change Prev Close Percentage'].fillna(0) #/ 100
                    cumulative_return = (1 + daily_returns).prod() - 1
                    
                    # Calculate position value
                    position_value = position['investment'] * (1 + cumulative_return)
                    cash += position_value
                    
                    print(f"SELL {symbol}: Investment {position['investment']:.2f} -> {position_value:.2f} (Return: {cumulative_return*100:.2f}%)")
                else:
                    # Fallback: if no data, return original investment
                    cash += position['investment']
                    print(f"SELL {symbol}: No price data, returning investment {position['investment']:.2f}")
            
            del active_positions[symbol]
        
        # Check for buys (new positions opening)
        if current_date in trades_by_date:
            trades_today = trades_by_date[current_date]
            capital_per_trade = cash / len(trades_today)
            
            print(f"\n{current_date.date()}: Opening {len(trades_today)} positions, {capital_per_trade:.2f} EUR each")
            
            for trade in trades_today:
                symbol = trade['Symbol']
                event_date = trade['EventDate']
                
                # Check if sheet exists
                if symbol not in excel_file.sheet_names:
                    print(f"Warning: Sheet '{symbol}' not found")
                    continue
                
                # Read stock data
                stock_df = pd.read_excel(excel_file, sheet_name=symbol)
                stock_df['Date'] = pd.to_datetime(stock_df['Date'])
                stock_df = stock_df.sort_values('Date')
                
                # Find actual buy date
                buy_data = stock_df[stock_df['Date'] == current_date]
                if buy_data.empty:
                    buy_data = stock_df[stock_df['Date'] >= current_date].head(1)
                
                if buy_data.empty:
                    print(f"Warning: Could not find buy date for {symbol}")
                    continue
                
                actual_buy_date = buy_data.iloc[0]['Date']
                
                # Find actual sell date
                sell_data = stock_df[stock_df['Date'] == event_date]
                if sell_data.empty:
                    sell_data = stock_df[stock_df['Date'] >= event_date].head(1)
                
                if sell_data.empty:
                    print(f"Warning: Could not find sell date for {symbol}")
                    continue
                
                actual_sell_date = sell_data.iloc[0]['Date']
                
                # Record position
                active_positions[symbol] = {
                    'investment': capital_per_trade,
                    'buy_date': actual_buy_date,
                    'sell_date': actual_sell_date
                }
                
                cash -= capital_per_trade
                print(f"BUY {symbol}: Invested {capital_per_trade:.2f}, Exit planned for {actual_sell_date.date()}")
        
        # Record portfolio value (cash + value of active positions)
        total_value = cash
        
        # Estimate current value of active positions
        for symbol, position in active_positions.items():
            stock_df = pd.read_excel(excel_file, sheet_name=symbol)
            stock_df['Date'] = pd.to_datetime(stock_df['Date'])
            stock_df = stock_df.sort_values('Date')
            
            # Get returns from buy date to current date
            date_range = stock_df[(stock_df['Date'] > position['buy_date']) & 
                                 (stock_df['Date'] <= current_date)]
            
            if not date_range.empty and 'Change Prev Close Percentage' in date_range.columns:
                daily_returns = date_range['Change Prev Close Percentage'].fillna(0) / 100
                cumulative_return = (1 + daily_returns).prod() - 1
                position_value = position['investment'] * (1 + cumulative_return)
                total_value += position_value
            else:
                total_value += position['investment']
        
        portfolio_timeline.append({
            'Date': current_date,
            'Value': total_value,
            'Cash': cash,
            'Positions': len(active_positions)
        })
    
    return portfolio_timeline, total_value

# Read the Excel file with all stock data
excel_file = pd.ExcelFile('sve_dionice_merged_EUR_filled.xlsx')
print(f"Found {len(excel_file.sheet_names)} sheets in Excel file")

initial_capital = 10000  # Starting with 10,000 EUR

# Process INSERTIONS portfolio
insertions_timeline, insertions_final = process_portfolio('INSERTIONS_ANN_EVENT.csv', excel_file, initial_capital)

# Process DELETIONS portfolio
deletions_timeline, deletions_final = process_portfolio('DELETIONS_ANN_EVENT.csv', excel_file, initial_capital)

# Create the plots
fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# Process INSERTIONS
if insertions_timeline:
    portfolio_df = pd.DataFrame(insertions_timeline)
    portfolio_df['Return_Pct'] = ((portfolio_df['Value'] / initial_capital) - 1) * 100
    
    # INSERTIONS - Portfolio value
    axes[0, 0].plot(portfolio_df['Date'], portfolio_df['Value'], linewidth=2, color='blue')
    axes[0, 0].axhline(y=initial_capital, color='r', linestyle='--', label='Initial Capital')
    axes[0, 0].set_xlabel('Date', fontsize=12)
    axes[0, 0].set_ylabel('Portfolio Value (EUR)', fontsize=12)
    axes[0, 0].set_title('INSERTIONS - Portfolio Value Over Time', fontsize=14, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # INSERTIONS - Cumulative returns
    axes[1, 0].plot(portfolio_df['Date'], portfolio_df['Return_Pct'], linewidth=2, color='green')
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
    
    print("\n" + "="*50)
    print("INSERTIONS PORTFOLIO PERFORMANCE")
    print("="*50)
    print(f"Initial Capital:    {initial_capital:,.2f} EUR")
    print(f"Final Value:        {insertions_final:,.2f} EUR")
    print(f"Total Return:       {total_return:,.2f}%")
    print("="*50)

# Process DELETIONS
if deletions_timeline:
    portfolio_df = pd.DataFrame(deletions_timeline)
    portfolio_df['Return_Pct'] = ((portfolio_df['Value'] / initial_capital) - 1) * 100
    
    # DELETIONS - Portfolio value
    axes[0, 1].plot(portfolio_df['Date'], portfolio_df['Value'], linewidth=2, color='purple')
    axes[0, 1].axhline(y=initial_capital, color='r', linestyle='--', label='Initial Capital')
    axes[0, 1].set_xlabel('Date', fontsize=12)
    axes[0, 1].set_ylabel('Portfolio Value (EUR)', fontsize=12)
    axes[0, 1].set_title('DELETIONS - Portfolio Value Over Time', fontsize=14, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # DELETIONS - Cumulative returns
    axes[1, 1].plot(portfolio_df['Date'], portfolio_df['Return_Pct'], linewidth=2, color='orange')
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
    
    print("\n" + "="*50)
    print("DELETIONS PORTFOLIO PERFORMANCE")
    print("="*50)
    print(f"Initial Capital:    {initial_capital:,.2f} EUR")
    print(f"Final Value:        {deletions_final:,.2f} EUR")
    print(f"Total Return:       {total_return:,.2f}%")
    print("="*50)

plt.tight_layout()
plt.savefig('portfolio_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nGraphs saved to 'portfolio_comparison.png'")
print("Detailed results saved to 'insertions_portfolio_results.csv' and 'deletions_portfolio_results.csv'")
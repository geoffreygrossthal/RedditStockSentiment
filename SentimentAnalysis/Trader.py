import os
import traceback
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class TradingStrategy:
    def __init__(self, buy_threshold=50, sell_threshold=-50):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.positions = {}
        self.trades = []
        self.reset_metrics()
        
    def reset_metrics(self):
        self.initial_capital = 100000
        self.current_capital = self.initial_capital
        self.wins = 0
        self.losses = 0
        self.daily_returns = []
        self.portfolio_values = []
        
    def generate_signal(self, sentiment_score):
        if sentiment_score >= self.buy_threshold:
            return 'BUY'
        elif sentiment_score <= self.sell_threshold:
            return 'SELL'
        return 'HOLD'
    
    def execute_trade(self, ticker, signal, price, date):
        if signal == 'BUY' and ticker not in self.positions:
            shares = self.current_capital // price
            cost = shares * price
            self.current_capital -= cost
            self.positions[ticker] = {'shares': shares, 'cost_basis': price}
            
            self.trades.append({
                'date': date,
                'ticker': ticker,
                'action': 'BUY',
                'shares': shares,
                'price': price,
                'value': cost
            })
            
        elif signal == 'SELL' and ticker in self.positions:
            position = self.positions[ticker]
            proceeds = position['shares'] * price
            self.current_capital += proceeds
            
            cost_basis = position['shares'] * position['cost_basis']
            if proceeds > cost_basis:
                self.wins += 1
            else:
                self.losses += 1
                
            self.trades.append({
                'date': date,
                'ticker': ticker,
                'action': 'SELL',
                'shares': position['shares'],
                'price': price,
                'value': proceeds
            })
            
            del self.positions[ticker]
    
    def backtest(self, ticker, sentiment_df, start_date=None, end_date=None):
        self.reset_metrics()
        
        # Download historical price data
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        print("\nStock data columns:", stock_data.columns)  # Debug print
        
        # Use 'Close' instead of 'Adj Close'
        price_data = stock_data['Close'].reset_index()
        price_data.columns = ['Date', 'price']
        
        # Merge sentiment and price data
        merged_data = pd.merge(
            sentiment_df,
            price_data,
            left_on='date',
            right_on='Date',
            how='inner'
        )
        merged_data = merged_data.sort_values('date')
        
        print(f"\nMerged data sample:\n{merged_data.head()}")  # Debug print
        
        # Run simulation
        for idx, row in merged_data.iterrows():
            date = row['date']
            sentiment = row['sentiment_score']
            price = row['price']
            
            signal = self.generate_signal(sentiment)
            self.execute_trade(ticker, signal, price, date)
            
            portfolio_value = self.current_capital
            if ticker in self.positions:
                portfolio_value += self.positions[ticker]['shares'] * price
            self.portfolio_values.append(portfolio_value)
            
            if len(self.portfolio_values) > 1:
                daily_return = (portfolio_value / self.portfolio_values[-2]) - 1
                self.daily_returns.append(daily_return)
    
    def calculate_metrics(self):
        if not self.portfolio_values:
            return {
                'Error': 'No trading data available'
            }
            
        final_value = self.portfolio_values[-1]
        roi = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        win_loss_ratio = self.wins / max(1, self.losses)
        
        if not self.daily_returns:
            return {
                'ROI (%)': round(roi, 2),
                'Win/Loss Ratio': round(win_loss_ratio, 2),
                'Total Trades': len(self.trades),
                'Winning Trades': self.wins,
                'Losing Trades': self.losses,
                'Note': 'Insufficient data for Sharpe ratio and drawdown calculations'
            }
        
        rf_rate = 0.02
        daily_rf_rate = (1 + rf_rate) ** (1/252) - 1
        excess_returns = np.array(self.daily_returns) - daily_rf_rate
        
        if len(excess_returns) > 1 and np.std(excess_returns) > 0:
            sharpe_ratio = np.sqrt(252) * (np.mean(excess_returns) / np.std(excess_returns))
        else:
            sharpe_ratio = 0
        
        cumulative_returns = np.array(self.portfolio_values) / self.initial_capital
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (running_max - cumulative_returns) / running_max
        max_drawdown = np.max(drawdowns) * 100 if len(drawdowns) > 0 else 0
        
        return {
            'ROI (%)': round(roi, 2),
            'Win/Loss Ratio': round(win_loss_ratio, 2),
            'Sharpe Ratio': round(sharpe_ratio, 2),
            'Maximum Drawdown (%)': round(max_drawdown, 2),
            'Total Trades': len(self.trades),
            'Winning Trades': self.wins,
            'Losing Trades': self.losses
        }
    
    def plot_results(self):
        if not self.trades or not self.portfolio_values:
            print("No trading data available for plotting")
            return
            
        dates = pd.date_range(start=self.trades[0]['date'], 
                            periods=len(self.portfolio_values), 
                            freq='B')
        
        plt.figure(figsize=(15, 7))
        plt.plot(dates, self.portfolio_values, label='Portfolio Value')
        
        buy_points = [(t['date'], t['value']) for t in self.trades if t['action'] == 'BUY']
        if buy_points:
            buy_dates, buy_values = zip(*buy_points)
            plt.scatter(buy_dates, buy_values, color='green', marker='^', 
                       label='Buy', s=100)
        
        sell_points = [(t['date'], t['value']) for t in self.trades if t['action'] == 'SELL']
        if sell_points:
            sell_dates, sell_values = zip(*sell_points)
            plt.scatter(sell_dates, sell_values, color='red', marker='v', 
                       label='Sell', s=100)
        
        plt.title('Portfolio Value Over Time')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def generate_sample_sentiment_data(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')
    
    n_days = len(date_range)
    sentiment_scores = np.zeros(n_days)
    sentiment_scores[0] = np.random.normal(0, 30)
    
    for i in range(1, n_days):
        mean_reversion = -0.1 * sentiment_scores[i-1]
        random_walk = np.random.normal(0, 15)
        sentiment_scores[i] = sentiment_scores[i-1] + mean_reversion + random_walk
    
    sentiment_scores = np.clip(sentiment_scores, -100, 100)
    
    return pd.DataFrame({
        'date': date_range,
        'sentiment_score': sentiment_scores
    })

def analyze_thresholds(ticker, sentiment_data, start_date, end_date):
    """
    Test different sentiment threshold combinations and analyze their performance.
    """
    # Test various threshold combinations
    threshold_pairs = [
        (30, -30),   # Moderate thresholds
        (50, -50),   # Current thresholds
        (70, -70),   # Aggressive thresholds
        (20, -20),   # Conservative thresholds
        (40, -40)    # Medium thresholds
    ]
    
    results = []
    
    for buy_threshold, sell_threshold in threshold_pairs:
        print(f"\nTesting thresholds - Buy: {buy_threshold}, Sell: {sell_threshold}")
        
        # Initialize and run strategy with these thresholds
        strategy = TradingStrategy(buy_threshold=buy_threshold, sell_threshold=sell_threshold)
        strategy.backtest(ticker, sentiment_data, start_date, end_date)
        metrics = strategy.calculate_metrics()
        
        # Add thresholds to metrics
        metrics['Buy Threshold'] = buy_threshold
        metrics['Sell Threshold'] = sell_threshold
        results.append(metrics)
    
    # Convert results to DataFrame for easy comparison
    results_df = pd.DataFrame(results)
    
    # Save results
    results_df.to_csv(f'../Data/{ticker}/sentiment_analysis/{ticker}_threshold_analysis.csv', index=False)
    
    return results_df

if __name__ == "__main__":
    # Test parameters
    start_date = '2017-01-01'
    end_date = '2023-12-31'
    buy_threshold = 50
    sell_threshold = -50
    
    # List of tickers from your data directory
    tickers = [
        'AAPL', 'AMZN', 'GOOGL', 'Meta', 'MSFT', 
        'NFLX', 'NVDA', 'TSLA', 'V', 'JPM'
    ]
    
    # Store results for all tickers
    all_results = []
    
    # Create figure for comparing all stocks
    plt.figure(figsize=(15, 10))
    
    for ticker in tickers:
        print(f"\nProcessing {ticker}...")
        
        try:
            # Load sentiment data
            sentiment_file = f'../Data/{ticker}/sentiment_analysis/{ticker}_sentiment_analysis.csv'
            if not os.path.exists(sentiment_file):
                print(f"No sentiment data found for {ticker}, skipping...")
                continue
                
            sentiment_data = pd.read_csv(sentiment_file)
            sentiment_data['date'] = pd.to_datetime(sentiment_data['date'])
            
            # Fill missing dates
            date_range = pd.date_range(start=sentiment_data['date'].min(), 
                                     end=sentiment_data['date'].max(), 
                                     freq='B')
            full_sentiment = pd.DataFrame({'date': date_range})
            sentiment_data = pd.merge(full_sentiment, sentiment_data, on='date', how='left')
            sentiment_data['sentiment_score'] = sentiment_data['sentiment_score'].fillna(0)
            
            # Initialize and run strategy
            strategy = TradingStrategy(buy_threshold=buy_threshold, sell_threshold=sell_threshold)
            strategy.backtest(ticker, sentiment_data, start_date, end_date)
            
            # Get metrics
            metrics = strategy.calculate_metrics()
            metrics['Ticker'] = ticker
            all_results.append(metrics)
            
            # Plot normalized portfolio value
            portfolio_values = np.array(strategy.portfolio_values)
            normalized_values = portfolio_values / portfolio_values[0]
            dates = pd.date_range(start=strategy.trades[0]['date'], 
                                periods=len(portfolio_values), 
                                freq='B')
            
            plt.plot(dates, normalized_values, label=ticker)
            
            # Save individual ticker results
            results_df = pd.DataFrame(strategy.trades)
            if not results_df.empty:
                os.makedirs(f'../Data/{ticker}/sentiment_analysis', exist_ok=True)
                results_df.to_csv(f'../Data/{ticker}/sentiment_analysis/{ticker}_trading_signals.csv', 
                                index=False)
            
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            traceback.print_exc()
    
    # Save combined metrics
    if all_results:
        combined_metrics = pd.DataFrame(all_results)
        combined_metrics = combined_metrics.sort_values('ROI (%)', ascending=False)
        
        print("\nCombined Results for All Tickers:")
        print(combined_metrics.to_string())
        
        combined_metrics.to_csv('../Data/combined_trading_metrics.csv', index=False)
        
        # Finalize and save comparison plot
        plt.title('Normalized Portfolio Value Comparison')
        plt.xlabel('Date')
        plt.ylabel('Normalized Portfolio Value')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('../Data/portfolio_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print summary statistics
        print("\nSummary Statistics:")
        print(f"Best Performing Stock: {combined_metrics.iloc[0]['Ticker']} (ROI: {combined_metrics.iloc[0]['ROI (%)']}%)")
        print(f"Average ROI: {combined_metrics['ROI (%)'].mean():.2f}%")
        print(f"Average Sharpe Ratio: {combined_metrics['Sharpe Ratio'].mean():.2f}")
        print(f"Average Maximum Drawdown: {combined_metrics['Maximum Drawdown (%)'].mean():.2f}%")
        
        # Optional: Calculate correlation between stocks' performance
        returns_data = {}
        for ticker in tickers:
            try:
                strategy = TradingStrategy()
                strategy.backtest(ticker, sentiment_data, start_date, end_date)
                returns_data[ticker] = strategy.daily_returns
            except:
                continue
                
        if len(returns_data) > 1:
            returns_df = pd.DataFrame(returns_data)
            correlation = returns_df.corr()
            correlation.to_csv('../Data/returns_correlation.csv')
    
    else:
        print("No results generated for any tickers.")
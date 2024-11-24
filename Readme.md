# Stock Market Sentiment Analysis Project
A Python-based system for analyzing social media sentiment's impact on stock market movements.

## Project Overview
This project implements a sentiment analysis and trading strategy system that:
1. Collects social media data from platforms like Reddit
2. Analyzes sentiment of stock-related posts 
3. Generates trading signals based on sentiment scores
4. Backtests trading strategies using historical stock data
5. Provides performance metrics and visualizations


## Prerequisites
- Python 3.8+
- Reddit API credentials (client ID and secret)
- Sufficient disk space for data storage


## Usage

### 1. Data Collection
Collect Reddit posts for specified stock tickers:
```bash
python src/PrawProxy.py
```
This will:
- Scrape posts from specified subreddits (stocks, wallstreetbets, investing)
- Filter for stock-related content
- Save posts in a hierarchical folder structure by date

### 2. Sentiment Analysis
Process collected posts and generate sentiment scores:
```bash
python src/SentimentAnalyzer.py
```
Features:
- Uses VADER or FinBERT for sentiment analysis
- Generates daily sentiment scores (-100 to 100)
- Considers post popularity and engagement metrics
- Saves results in CSV format

### 3. Trading Strategy Backtesting
Test trading strategies based on sentiment scores:
```bash
python src/TradingTickers.py
```
Functionality:
- Implements sentiment-based trading signals
- Backtests strategies with historical price data
- Calculates performance metrics (ROI, Sharpe ratio, etc.)
- Generates visualization plots

## Configuration Options

### Sentiment Analysis
- `model_type`: Choose between 'vader' or 'finbert'
- `data_root`: Root directory for data storage
- Logging configuration in `sentiment_analysis.log`

### Trading Strategy
- `buy_threshold`: Sentiment score threshold for buy signals (default: 50)
- `sell_threshold`: Sentiment score threshold for sell signals (default: -50)
- `initial_capital`: Starting capital for backtesting (default: $100,000)

## Output Files
The system generates several output files:
- `{TICKER}_sentiment.json`: Daily sentiment scores
- `{TICKER}_trading_signals.csv`: Trading decisions and results
- `{TICKER}_threshold_analysis.csv`: Performance metrics for different thresholds
- `portfolio_comparison.png`: Visualization of strategy performance
- `combined_trading_metrics.csv`: Aggregated results across all tickers

## Performance Metrics
The backtesting system calculates:
- Return on Investment (ROI)
- Win/Loss Ratio
- Sharpe Ratio
- Maximum Drawdown
- Total number of trades
- Success rate of trades
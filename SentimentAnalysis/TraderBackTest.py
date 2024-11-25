import os
import json
import logging
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

# Set up logging configuration
log_filename = "trading_decisions.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, 
                    format="%(asctime)s - %(message)s", filemode='a')

def get_user_input_for_thresholds():
    # Get the buy threshold from the user
    while True:
        try:
            buy_threshold = float(input("Enter the buy threshold (e.g., 50): "))
            break  # Exit the loop if input is valid
        except ValueError:
            print("Invalid input. Please enter a numeric value for the buy threshold.")
    
    # Get the sell threshold from the user
    while True:
        try:
            sell_threshold = float(input("Enter the sell threshold (e.g., -50): "))
            break  # Exit the loop if input is valid
        except ValueError:
            print("Invalid input. Please enter a numeric value for the sell threshold.")

def get_user_input_for_thresholds():
    # Get the buy threshold from the user
    while True:
        try:
            buy_threshold = float(input("Enter the buy threshold (e.g., 50): "))
            break  # Exit the loop if input is valid
        except ValueError:
            print("Invalid input. Please enter a numeric value for the buy threshold.")

    # Get the sell threshold from the user
    while True:
        try:
            sell_threshold = float(input("Enter the sell threshold (e.g., -50): "))
            break  # Exit the loop if input is valid
        except ValueError:
            print("Invalid input. Please enter a numeric value for the sell threshold.")
    
    return buy_threshold, sell_threshold

def get_sentiment_recommendation(stock_ticker, date, buy_threshold, sell_threshold):
    # Define the folder and file path where sentiment data is stored
    folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SentimentScoreDataAAPL')
    file_path = os.path.join(folder_path, f"{stock_ticker}_{date}.json")
    
    print(f"Looking for sentiment data at: {file_path}")  # Debugging line
    
    # Check if the sentiment data file exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            existing_data = json.load(f)  # The file should contain a single JSON object
        
        # Ensure that the data has the correct structure
        if "date" in existing_data and "sentiment_score" in existing_data:
            sentiment_score = existing_data["sentiment_score"]
            
            # Determine recommendation based on sentiment score and thresholds
            if sentiment_score >= buy_threshold:
                trading_decision = "buy"
            elif sentiment_score <= sell_threshold:
                trading_decision = "sell"
            else:
                trading_decision = "hold"

            # Log the trading decision and other information
            log_trading_decision(date, sentiment_score, buy_threshold, sell_threshold, trading_decision)
        else:
            print(f"Data format error: The file {file_path} does not contain the expected keys.")
    else:
        print(f"No sentiment data file found for {stock_ticker} on {date} at {file_path}")
    
    # Default trading decision if no matching data is found
    trading_decision = "hold"
    log_trading_decision(date, None, buy_threshold, sell_threshold, trading_decision)
    return trading_decision


def log_trading_decision(date, sentiment_score, buy_threshold, sell_threshold, trading_decision):
    # Log the decision along with parameters in a structured format
    log_entry = {
        "date": date,
        "sentiment_score": sentiment_score if sentiment_score is not None else "N/A",
        "buy_threshold": buy_threshold,
        "sell_threshold": sell_threshold,
        "trading_decision": trading_decision
    }
    logging.info(json.dumps(log_entry))

def run_backtest(stock_ticker, buy_threshold, sell_threshold, start_date, end_date):
    # Fetch historical stock data from Yahoo Finance
    stock_data = yf.download(stock_ticker, start=start_date, end=end_date)
    
    # Backtest logic variables
    cash = 10000  # Start with $10,000
    shares = 0
    portfolio_value = []
    
    # Initial Buy: Buy into the stock on the first day with all available cash
    first_day_price = stock_data.iloc[0]['Close']  # Get the closing price on the first day
    shares = cash // first_day_price  # Buy as many shares as possible with the available cash
    cash -= shares * first_day_price  # Subtract the cash used for the purchase

    # Calculate the portfolio value for the first day
    portfolio_value.append(cash + shares * first_day_price)
    
    # Backtest logic: iterate through the stock data from the second day onwards
    for date, row in stock_data.iloc[1:].iterrows():
        price = row['Close']
        
        # Get the sentiment-based action for the current date (ensure it's a single value)
        action = get_sentiment_recommendation(stock_ticker, date.strftime('%Y-%m-%d'), buy_threshold, sell_threshold)

        # Ensure action is a single value (no ambiguity)
        action = action.item() if isinstance(action, pd.Series) else action
        
        if action == 'buy' and cash >= price:
            # Buy shares if we have enough cash
            shares_to_buy = cash // price
            shares += shares_to_buy
            cash -= shares_to_buy * price
        elif action == 'sell' and shares > 0:
            # Sell all shares if we have any
            cash += shares * price
            shares = 0
        
        # Calculate portfolio value: cash + value of remaining shares
        portfolio_value.append(cash + shares * price)
    
    # Calculate your portfolio's cumulative return
    initial_value = portfolio_value[0]
    portfolio_return = [(x / initial_value - 1) * 100 for x in portfolio_value]

    # Fetch Apple's historical adjusted closing price
    apple_data = yf.download("AAPL", start=start_date, end=end_date)
    
    # Calculate Apple's cumulative return
    apple_returns = apple_data['Adj Close'].pct_change().cumsum() * 100

    # Plot the results
    plt.figure(figsize=(14, 7))
    plt.plot(stock_data.index, portfolio_return, label="Backtest Portfolio", color='blue')
    plt.plot(apple_returns.index, apple_returns, label="AAPL Stock", color='red')
    plt.title(f"Backtest Performance vs AAPL Returns ({start_date} to {end_date})")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return (%)")
    plt.legend(loc="best")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# Main function to run the program
if __name__ == "__main__":
    print("The stock ticker is always set to AAPL")
    date = input("Enter the date for sentiment analysis (YYYY-MM-DD): ").strip()
    buy_threshold, sell_threshold = get_user_input_for_thresholds()
    recommendation = get_sentiment_recommendation("AAPL", date, buy_threshold, sell_threshold)
    print(f"Recommendation for AAPL on {date}: {recommendation}")
    while True:
        print()
        user_input = input("Would you like to run a backtest with historical sentiment scores? (y/n): ").strip().lower()
        if user_input == 'y':
            print("Running backtest with historical sentiment scores...") 
            start_date = "2014-01-01"
            end_date = datetime.today().strftime('%Y-%m-%d')
            print("The stock ticker is always set to AAPL")
            buy_threshold, sell_threshold = get_user_input_for_thresholds()
            run_backtest("AAPL", buy_threshold, sell_threshold, start_date, end_date)
            print("Backtest completed with updated Historical Sentiment Score")
            break
        elif user_input == 'n':
            print("Skipping backtest.")
            break
        else:
            print("Invalid input. Please enter 'y' for Yes or 'n' for No.")



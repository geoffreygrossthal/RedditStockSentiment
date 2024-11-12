import json
import praw
import time
import sys
import os
import re
from datetime import datetime, timezone, timedelta

# Ensure that the root path and other necessary paths are included
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_path)

from DataModels.RedditPost import RedditPost

# Load configuration from the specified path in PathsConfig
config_path = os.path.join(os.path.dirname(__file__), 'PrawConfig.json')
with open(config_path) as config_file:
    config = json.load(config_file)

# Add the data models path to sys.path if needed
data_models_path = os.path.join(os.path.dirname(__file__), 'DataModels')
sys.path.append(data_models_path)

# Configure Reddit API credentials using the loaded config
reddit = praw.Reddit(
    client_id=config['reddit']['client_id'],
    client_secret=config['reddit']['client_secret'],
    user_agent=config['reddit']['user_agent'],
)

# Define the list of stock tickers
stock_tickers = [
    {"ticker": "AAPL", "name": "Apple"},
    {"ticker": "TSLA", "name": "Tesla"},
    {"ticker": "MSFT", "name": "Microsoft"},
    {"ticker": "AMZN", "name": "Amazon"},
    {"ticker": "GOOGL", "name": "Alphabet"},
    {"ticker": "FB", "name": "Meta"},
    {"ticker": "NFLX", "name": "Netflix"},
    {"ticker": "NVDA", "name": "NVIDIA"},
    {"ticker": "BRK.B", "name": "Berkshire"},
    {"ticker": "JPM", "name": "JPMorgan"},
    {"ticker": "V", "name": "Visa"},
    {"ticker": "PG", "name": "Procter & Gamble"},
    {"ticker": "DIS", "name": "Disney"},
    {"ticker": "PYPL", "name": "PayPal"},
    {"ticker": "INTC", "name": "Intel"}
]

# Function to check if a post contains any of the stock tickers
def contains_stock_ticker(post, stock_tickers):
    tickers = [ticker["ticker"] for ticker in stock_tickers]
    names = [ticker["name"] for ticker in stock_tickers]
    search_terms = tickers + names
    ticker_pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, search_terms)) + r')\b', re.IGNORECASE)
    matched_tickers = []
    if ticker_pattern.search(post.title) or ticker_pattern.search(post.content):
        matched_tickers = [ticker["ticker"] for ticker in stock_tickers if ticker_pattern.search(post.title) or ticker_pattern.search(post.content)]
    return matched_tickers

# Function to fetch posts based on subreddit and time filter
def get_posts(subreddit_name, time_filter, limit):
    
    # Get valid time filter
    valid_time_filters = {"all", "day", "hour", "month", "week", "year"}
    if time_filter not in valid_time_filters:
        raise ValueError(f"Invalid time_filter: {time_filter}. Must be one of {valid_time_filters}.")
    subreddit = reddit.subreddit(subreddit_name)

    # Filter subreddit based off of interval
    if time_filter == "all":
        submissions = list(subreddit.top(limit=limit))
    elif time_filter == "day":
        submissions = list(subreddit.top(time_filter="day", limit=limit))
    elif time_filter == "week":
        submissions = list(subreddit.top(time_filter="week", limit=limit))
    elif time_filter == "month":
        submissions = list(subreddit.top(time_filter="month", limit=limit))
    elif time_filter == "year":
        submissions = list(subreddit.top(time_filter="year", limit=limit))
    else:
        submissions = list(subreddit.top(time_filter="hour", limit=limit))
    print(f"Found {len(submissions)} posts.")
    for submission in submissions:
        post = RedditPost(
            title=submission.title,
            score=submission.score,
            url=submission.url,
            content=submission.selftext,
            created_utc=submission.created_utc,
            subreddit_name=subreddit_name,
            comments=submission.num_comments
        )
        matched_tickers = contains_stock_ticker(post, stock_tickers)
        if matched_tickers:
            for ticker in matched_tickers:
                if not post_saved(post, ticker):
                    insert_reddit_post_into_folders(post, ticker)
                else:
                    print(f"Post for {ticker} already saved.")
        else:
            print("No relevant ticker found in post.")

# Function to insert the RedditPost into the folder structure and save as JSON
def insert_reddit_post_into_folders(reddit_post, stock_ticker):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data'))
    created_date = datetime.fromtimestamp(reddit_post.created_utc, timezone.utc)
    year = created_date.year
    month = created_date.month
    day = created_date.day
    folder_path = os.path.join(base_dir, stock_ticker, str(year), f"{month:02d}", f"{day:02d}")
    file_path = os.path.join(folder_path, "RedditPosts.json")
    os.makedirs(folder_path, exist_ok=True)
    if os.path.exists(file_path):
        with open(file_path, 'r+', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            data.append(reddit_post.to_dict())
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Reddit post for {stock_ticker} appended to {file_path}")
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([reddit_post.to_dict()], f, ensure_ascii=False, indent=4)
        print(f"Reddit post for {stock_ticker} saved as new JSON at {file_path}")
    time.sleep(1)

# Function to see if the data has already been saved
def post_saved(reddit_post, stock_ticker):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data'))
    created_date = datetime.fromtimestamp(reddit_post.created_utc, timezone.utc)
    year = created_date.year
    month = created_date.month
    day = created_date.day
    folder_path = os.path.join(base_dir, stock_ticker, str(year), f"{month:02d}", f"{day:02d}")
    file_path = os.path.join(folder_path, "RedditPosts.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            for post in data:
                if post.get('url') == reddit_post.url:
                    return True
    return False

# Loop through each day from Nov 8, 2024, going back 10 years
subreddit_names = ["stocks", "wallstreetbets", "investing", "stocks"]

for subreddit_name in subreddit_names:
    posts_for_date = get_posts(subreddit_name=subreddit_name, time_filter='all', limit=3000)
    if posts_for_date:
        print(f"Found {len(posts_for_date)} posts for {subreddit_name}.")
    else:
        print(f"No posts found for {subreddit_name}.")
    time.sleep(1)
    print()
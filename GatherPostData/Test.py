import os
import json
import random
import praw
import datetime

# Define a data model for the Reddit Post
class RedditPost:
    def __init__(self, title, score, url, content, created_utc, subreddit_name, comments):
        self.title = title
        self.score = score
        self.url = url
        self.content = content
        self.created_utc = created_utc
        self.subreddit_name = subreddit_name
        self.comments = comments

    def to_dict(self):
        return {
            "title": self.title,
            "score": self.score,
            "url": self.url,
            "content": self.content,
            "created_utc": self.created_utc,
            "subreddit_name": self.subreddit_name,
            "comments": self.comments
        }

# Function to insert the RedditPost into the folder structure and save as JSON
def insert_reddit_post_into_folders(reddit_post, stock_ticker):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data'))
    created_date = datetime.datetime.fromtimestamp(reddit_post.created_utc, datetime.timezone.utc)
    year = created_date.year
    month = created_date.month
    day = created_date.day
    folder_path = os.path.join(base_dir, stock_ticker, str(year), f"{month:02d}", f"{day:02d}")
    file_path = os.path.join(folder_path, "RedditPosts.json")

    print(f"Folder Path: {folder_path}")
    print(f"File Path: {file_path}")
    
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

# Simulate a function to create random RedditPost data
def create_mock_reddit_post(stock_ticker, subreddit_name):
    # Randomized Reddit post data for testing
    title = f"Random post about {stock_ticker}"
    score = random.randint(0, 1000)
    url = f"https://www.reddit.com/r/{subreddit_name}/comments/{random.randint(100000, 999999)}/"
    content = f"Some content for {stock_ticker} post"
    created_utc = random.randint(1577836800, 1672531199)  # Random date between 2020 and 2022
    comments = [{"author": "user1", "content": "Interesting post!"}, {"author": "user2", "content": "I agree!"}]
    
    return RedditPost(title, score, url, content, created_utc, subreddit_name, comments)

# Test the function with different stock tickers and subreddits
def test_insert_reddit_post():
    stock_tickers = ['AAPL', 'TSLA', 'GOOG', 'AMZN', 'MSFT']
    subreddit_names = ['stocks', 'investing', 'wallstreetbets']

    for stock_ticker in stock_tickers:
        for subreddit_name in subreddit_names:
            # Generate a mock Reddit post for each combination of stock and subreddit
            reddit_post = create_mock_reddit_post(stock_ticker, subreddit_name)
            insert_reddit_post_into_folders(reddit_post, stock_ticker)

if __name__ == "__main__":
    test_insert_reddit_post()

import json
import praw
import time
import sys
import re
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

# Define AAPL and its key words
stock_tickers = [
    {
        "ticker": "AAPL",
        "keywords": [
            "AAPL", "aaple", "apple", "iphone", "Apple", "TimCook", "iPhone", "iPad", "MacBook", "AppleWatch", "AirPods", "AppleTV", 
            "iOS", "macOS", "iCloud", "AppStore", "ApplePay", "AppleCard", "AppleMusic", "AppleArcade", 
            "AppleFitness", "AppleNews", "AppleBooks", "iTunes", "AppleRetail", "AppleSilicon", 
            "M1Chip", "M2Chip", "iMac", "MacMini", "MacPro", "HomePod", "AirTags", "AppleCampus", 
            "AppleStore", "Airtime", "FaceID", "TouchID", "AppleCare", "AppStoreReview", "AppleDeveloper", 
            "iCloudDrive", "iMessage", "Siri", "AppleChip", "AppleEvent", "WWDC", "AppleEarnings", 
            "AppleStock", "AppleRevenue", "AppleGrowth", "AppleShareholder", "phone", "smartphone", 
            "tablet", "laptop", "desktop", "charger", "AirPodsPro", "iPhone13", "iPhone14", "iPhone15", 
            "AppleWatchSeries", "iPhoneX", "iPhoneSE", "MacOSVentura", "MacOSMonterey", "iPhoneSE", "MacOSBigSur"
        ]
    }
]

# Function to check if a post contains any of the keywords
def contains_keywords(post, stock_tickers):
    keyword_set = {keyword for ticker in stock_tickers for keyword in ticker['keywords']}
    keyword_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(keyword) for keyword in keyword_set) + r')\b', re.IGNORECASE)
    post_text = post.title + " " + post.content
    if keyword_pattern.search(post_text):
        return True
    return False


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

        if contains_keywords(post, stock_tickers):
            if not post_saved(post, "AAPL"):
                insert_reddit_post_into_folders(post, "AAPL")
            else:
                print(f"Post for AAPL already saved.")
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
    time.sleep(0.5)

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

# Subreddit names (finance + stock-related + popular news)
# subreddit_names = [
#     "stocks", "wallstreetbets", "investing",
#     "worldnews", "news", "technology"
# ]
subreddit_names = [
    "apple"
]

for subreddit_name in subreddit_names:
    get_posts(subreddit_name=subreddit_name, time_filter='month', limit=1000)
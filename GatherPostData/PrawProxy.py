import json
import praw
import sys
import os
from datetime import datetime, timezone

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

# Function to fetch posts based on subreddit and time filter
def get_posts(subreddit_name="wallstreetbets", time_filter="day", limit=100):
    valid_time_filters = {"all", "day", "hour", "month", "week", "year"}
    if time_filter not in valid_time_filters:
        raise ValueError(f"Invalid time_filter: {time_filter}. Must be one of {valid_time_filters}.")
    
    subreddit = reddit.subreddit(subreddit_name)
    
    # Fetch the posts
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
    
    print(f"Found {len(submissions)} posts.")  # Debugging line
    
    posts = []
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
        print(f"Title: {post.title}")
        print(f"Score: {post.score}")
        print(f"Comments: {post.comments}")
        print(f"URL: {post.url}")
        print(f"Created at: {datetime.fromtimestamp(post.created_utc, tz=timezone.utc)}")
        print('-' * 80)
        posts.append(post)
        insert_reddit_post_into_folders(post, "TSLA")
    
    return posts


# Adjusted function to fetch posts for a specific date
def get_posts_for_specific_date(subreddit_name="wallstreetbets", target_date=datetime(2024, 11, 4), limit=100):
    posts = get_posts(subreddit_name=subreddit_name, time_filter="day", limit=limit)
    start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0).timestamp()
    end_of_day = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59).timestamp()
    filtered_posts = [
        post for post in posts
        if start_of_day <= post.created_utc <= end_of_day
    ]
    return filtered_posts

# Function to insert the RedditPost into the folder structure and save as JSON
def insert_reddit_post_into_folders(reddit_post, stock_ticker):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data'))
    
    # Get the post creation date
    created_date = datetime.fromtimestamp(reddit_post.created_utc, timezone.utc)
    year = created_date.year
    month = created_date.month
    day = created_date.day

    # Define the folder path where the post will be inserted
    folder_path = os.path.join(base_dir, stock_ticker, str(year), f"{month:02d}", f"{day:02d}")

    # Create the folder structure if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Define the JSON file path
    file_path = os.path.join(folder_path, "RedditPosts.json")

    # Check if the file exists
    if os.path.exists(file_path):
        # If the file exists, read its contents and append the new post
        with open(file_path, 'r+', encoding='utf-8') as f:
            try:
                # Try to load existing data
                data = json.load(f)
            except json.JSONDecodeError:
                # If the file is empty or corrupted, start with an empty list
                data = []
            
            # Append the new post
            data.append(reddit_post.to_dict())

            # Move the file pointer to the beginning and save the updated data
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Reddit post for {stock_ticker} appended to {file_path}")
    else:
        # If the file doesn't exist, create a new file with the new post
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([reddit_post.to_dict()], f, ensure_ascii=False, indent=4)
        
        print(f"Reddit post for {stock_ticker} saved as new JSON at {file_path}")

# Function to see if the data has already been saved
def is_post_already_inserted(reddit_post, stock_ticker, base_dir):
    created_date = datetime.datetime.fromtimestamp(reddit_post.created_utc, datetime.timezone.utc)
    year = created_date.year
    month = created_date.month
    day = created_date.day
    folder_path = os.path.join(base_dir, stock_ticker, str(year), f"{month:02d}", f"{day:02d}")
    file_path = os.path.join(folder_path, f"RedditPost_{reddit_post.title[:10]}.json")
    if os.path.exists(file_path):
        print(f"Post with title '{reddit_post.title[:30]}...' already exists.")
        return True 
    else:
        print(f"Post with title '{reddit_post.title[:30]}...' does not exist yet.")
        return False

# Example usage: Get posts from 'wallstreetbets' on 11/4/2024
subreddit_name = "wallstreetbets"
target_date = datetime(2024, 11, 4)  # Nov 4, 2024
posts_for_date = get_posts_for_specific_date(subreddit_name=subreddit_name, target_date=target_date, limit=100)

# Display the filtered posts
for post in posts_for_date:
    print(f"Title: {post.title}")
    print(f"Score: {post.score}")
    print(f"Comments: {post.comments}")
    print(f"URL: {post.url}")
    print(f"Created at: {datetime.fromtimestamp(post.created_utc, tz=timezone.utc)}")
    print('-' * 80)

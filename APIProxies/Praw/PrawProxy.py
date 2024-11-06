import json
import praw
import sys
import os
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)
print(f"Current sys.path: {sys.path}")
from DataModels.RedditPost import RedditPost

# Load configuration from the specified path
with open(PathsConfig.PRAW_CONFIG) as config_file:
    config = json.load(config_file)

# Add the data models path to sys.path if needed
sys.path.append(PathsConfig.DATA_MODELS_PATH)

# Configure Reddit API credentials
reddit = praw.Reddit(
    client_id=config['reddit']['client_id'],
    client_secret=config['reddit']['client_secret'],
    user_agent=config['reddit']['user_agent'],
)

# Returns a list of posts given a sub reddit and time
def get_posts(subreddit_name="wallstreetbets", time_filter="day", limit=100):
    valid_time_filters = {"all", "day", "hour", "month", "week", "year"}
    if time_filter not in valid_time_filters:
        raise ValueError(f"Invalid time_filter: {time_filter}. Must be one of {valid_time_filters}.")

    subreddit = reddit.subreddit(subreddit_name)

    # Fetch posts based on the time filter
    if time_filter == "all":
        submissions = subreddit.top(limit=limit)
    elif time_filter == "day":
        submissions = subreddit.top(time_filter="day", limit=limit)
    elif time_filter == "week":
        submissions = subreddit.top(time_filter="week", limit=limit)
    elif time_filter == "month":
        submissions = subreddit.top(time_filter="month", limit=limit)
    elif time_filter == "year":
        submissions = subreddit.top(time_filter="year", limit=limit)
    else:
        submissions = subreddit.top(time_filter="hour", limit=limit)

    # Create data model instances
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
        posts.append(post)

    return posts

from datetime import datetime, timedelta

# Adjusted function to fetch posts for a specific date (11/4/2024)
def get_posts_for_specific_date(subreddit_name="wallstreetbets", target_date=datetime(2024, 11, 4), limit=100):
    # Use the 'get_posts' function to get the top posts for the 'day' time filter (last 24 hours)
    posts = get_posts(subreddit_name=subreddit_name, time_filter="day", limit=limit)

    # Convert target_date to a timestamp range (midnight UTC of 11/4/2024 to just before midnight of 11/5/2024)
    start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0).timestamp()
    end_of_day = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59).timestamp()

    # Filter posts based on created_utc timestamp for the specific day
    filtered_posts = [
        post for post in posts 
        if start_of_day <= post.created_utc <= end_of_day
    ]

    return filtered_posts

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
    print(f"Created at: {datetime.utcfromtimestamp(post.created_utc)}")
    print('-' * 80)

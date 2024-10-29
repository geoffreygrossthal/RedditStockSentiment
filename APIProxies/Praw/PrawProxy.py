import json
import praw
import sys
from Config import PathsConfig
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
def get_posts(subreddit_name, time_filter="all", limit=100):
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
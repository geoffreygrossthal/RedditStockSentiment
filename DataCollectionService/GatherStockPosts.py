import json
import praw
import sys
from Config import PathsConfig
from DataModels.RedditPost import RedditPost
from APIProxies import get_posts

def fetch_posts(subreddit_name, time_filter="all", limit=100):
    """Fetches posts from a subreddit."""
    try:
        # Call the function to get posts
        posts = get_posts(subreddit_name, time_filter, limit)
        return posts

    except ValueError as e:
        print(e)
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
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

    # Define your parameters
    subreddit_name = "wallstreetbets"  
    time_filter = "week"               
    limit = 100                         

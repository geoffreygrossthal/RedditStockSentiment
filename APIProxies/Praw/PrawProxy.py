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

# Specify the subreddit from the config file
subreddit_name = config['reddit']['wallstreetbets']
subreddit = reddit.subreddit(subreddit_name)

# Gather posts and create data model instances
posts = []
for submission in subreddit.new(limit=100):  # Adjust limit as needed
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

# Print the collected posts
for post in posts:
    print(post)


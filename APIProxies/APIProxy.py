import datetime
import praw

# Configure Reddit API credentials
reddit = praw.Reddit(
    client_id='wbqrtipDWMwrK-pIRyEr0A',
    client_secret='jCG35SefQR1WnwNvPCOD85lrDfLfmw',
    user_agent='YOUR_USER_AGENT SentimentGather/1.0 by RedditStockSentiment',
)

# Specify the subreddit (e.g., r/stocks, r/wallstreetbets)
subreddit_name = 'wallstreetbets'  # Change as needed
subreddit = reddit.subreddit(subreddit_name)

#Gather posts
for submission in subreddit.new(limit=100):  # Adjust limit as needed
    print(f"Title: {submission.title}")
    print(f"Score: {submission.score}")
    print(f"URL: {submission.url}")
    print(f"Content: {submission.selftext}")
    print(f"Created: {submission.created_utc}")
    created_date = datetime.datetime.fromtimestamp(submission.created_utc, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Created: {created_date}")
    print("------")

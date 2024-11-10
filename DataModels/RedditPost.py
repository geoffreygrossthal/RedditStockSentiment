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
        self.created_date = datetime.datetime.fromtimestamp(created_utc, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.subreddit_name = subreddit_name
        self.comments = comments

    def __repr__(self):
        return (f"RedditPost(title={self.title}, score={self.score}, url={self.url}, "
                f"created_date={self.created_date}, subreddit_name={self.subreddit_name})")
    
    # Add to_dict() method to return object as a dictionary
    def to_dict(self):
        return {
            "title": self.title,
            "score": self.score,
            "url": self.url,
            "content": self.content,
            "created_utc": self.created_utc,
            "created_date": self.created_date,
            "subreddit_name": self.subreddit_name,
            "comments": self.comments
        }
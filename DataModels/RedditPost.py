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

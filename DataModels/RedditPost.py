import praw
import datetime

# Define a data model for the Reddit submission
class RedditPost:
    def __init__(self, title, score, url, content, created_utc):
        self.title = title
        self.score = score
        self.url = url
        self.content = content
        self.created_utc = created_utc
        self.created_date = self.convert_created_date()

    def convert_created_date(self):
        return datetime.datetime.fromtimestamp(self.created_utc, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    def __repr__(self):
        return (f"RedditPost(title={self.title}, score={self.score}, "
                f"url={self.url}, created_date={self.created_date})")
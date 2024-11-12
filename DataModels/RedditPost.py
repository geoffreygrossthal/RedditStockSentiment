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
    
    def to_string(self):
        return (f"Title: {self.title}\n"
                f"Score: {self.score}\n"
                f"URL: {self.url}\n"
                f"Content: {self.content}\n"
                f"Created: {self.created_utc}\n"
                f"Subreddit: {self.subreddit_name}\n"
                f"Comments: {self.comments}\n")
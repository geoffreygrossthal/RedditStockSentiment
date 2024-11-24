import os
import json
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from SentimentAnalyzer import StockSentimentAnalyzer
import matplotlib.pyplot as plt
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GatherPostData.PrawProxy import run_data_collection

def load_posts_from_date(stock_ticker, year, month, day):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data'))
    folder_path = os.path.join(base_dir, stock_ticker, str(year), f"{month:02d}", f"{day:02d}")
    file_path = os.path.join(folder_path, "RedditPosts.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def get_latest_reddit_posts(stock_ticker, start_date=None, target_count=100):
    if start_date is None:
        start_date = datetime.now().date()
    posts = []
    current_date = start_date
    while len(posts) < target_count:
        year, month, day = current_date.year, current_date.month, current_date.day
        new_posts = load_posts_from_date(stock_ticker, year, month, day)
        
        if new_posts:
            posts.extend(new_posts)
            if len(posts) >= target_count:
                break
        
        current_date -= timedelta(days=1)  # Always move to the previous day if no posts or posts found
        
        # Termination condition: stop if we reach 2013
        if current_date.year <= 2013:
            break
    
    return posts[:target_count]

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_sentiment(post_text, analyzer=None):
    """Analyzes sentiment of the post_text using VADER SentimentIntensityAnalyzer"""
    if analyzer is None:
        analyzer = SentimentIntensityAnalyzer()  # Create a new instance if not provided
    
    # Get sentiment scores
    sentiment_scores = analyzer.polarity_scores(post_text)
    
    # Classify sentiment as positive, negative, or neutral
    if sentiment_scores['compound'] >= 0.05:
        sentiment = 'positive'
    elif sentiment_scores['compound'] <= -0.05:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return sentiment

def analyze_live_data(stock_ticker, date_to_analyze):
    """Run sentiment analysis on actual Reddit data."""
    data_root = "../Data"
    posts = get_latest_reddit_posts(stock_ticker, start_date=date_to_analyze)
    print(f"Found {len(posts)} posts to analyze for {date_to_analyze}.")
    analyzer = SentimentIntensityAnalyzer()
    post_sentiments = []
    for post in posts:
        post_text = post['title']
        if 'selftext' in post:
            post_text += " " + post['selftext']
        sentiment = analyze_sentiment(post_text, analyzer)
        post_sentiments.append({
            'post': post,
            'sentiment': sentiment
        })
        if len(post_sentiments) >= 100:
            print("Reached 100 posts, stopping analysis.")
            break
    for i, result in enumerate(post_sentiments):
        print(f"{i + 1}. Post: {result['post']['title']}\nSentiment: {result['sentiment']}\n")
    return post_sentiments

def calculate_sentiment_score_from_posts(post_sentiments):
    pos_posts = 0
    neg_posts = 0
    neutral_posts = 0
    for result in post_sentiments:
        sentiment = result['sentiment']
        if sentiment == 'positive':
            pos_posts += 1
        elif sentiment == 'negative':
            neg_posts += 1
        else:
            neutral_posts += 1
    if pos_posts == 0 and neg_posts == 0:
        return 0
    sentiment_score = ((pos_posts - neg_posts)/ (pos_posts + neg_posts)) * 100
    return sentiment_score


# Example usage
stock_ticker = "AAPL"
run_data_collection()
today_date = datetime.now().date()
post_sentiments = analyze_live_data(stock_ticker, today_date)
score = calculate_sentiment_score_from_posts(post_sentiments)
print(f"Sentiment Score for {stock_ticker} on {today_date}: {score}")

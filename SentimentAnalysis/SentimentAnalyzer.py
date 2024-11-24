import pandas as pd
import numpy as np
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from datetime import datetime
import logging
import os

class StockSentimentAnalyzer:
    def __init__(self, model_type="vader", data_root="../Data"):
        self.model_type = model_type
        self.data_root = data_root
        self.setup_logger()
        
        if model_type == "vader":
            self.analyzer = SentimentIntensityAnalyzer()
        elif model_type == "finbert":
            model_name = "ProsusAI/finbert"
            self.analyzer = pipeline("sentiment-analysis", model=model_name)
        else:
            raise ValueError("Unsupported model type. Use 'vader' or 'finbert'")

    def setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='sentiment_analysis.log'
        )
        self.logger = logging.getLogger(__name__)

    def load_posts_from_json(self, json_path):
        try:
            with open(json_path, 'r') as file:
                posts_data = json.load(file)
            
            if not isinstance(posts_data, list):
                posts_data = [posts_data]
                
            df = pd.DataFrame(posts_data)
            
            # Combine title and content for analysis
            df['full_text'] = df['title'] + ' ' + df['content'].fillna('')
            
            # Convert timestamp to datetime
            df['date'] = pd.to_datetime(df['created_utc'], unit='s')
            
            # Add metadata
            df['post_score'] = df['score']
            df['comment_count'] = df['comments']
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading {json_path}: {str(e)}")
            return pd.DataFrame()

    def analyze_text(self, text):
        if not isinstance(text, str):
            return {'compound': 0, 'classification': 'neutral'}
            
        try:
            if self.model_type == "vader":
                scores = self.analyzer.polarity_scores(text)
                if scores['compound'] >= 0.05:
                    classification = 'positive'
                elif scores['compound'] <= -0.05:
                    classification = 'negative'
                else:
                    classification = 'neutral'
                    
                return {
                    'compound': scores['compound'],
                    'classification': classification
                }
                
            elif self.model_type == "finbert":
                result = self.analyzer(text)[0]
                label_map = {
                    'positive': 'positive',
                    'negative': 'negative',
                    'neutral': 'neutral'
                }
                return {
                    'compound': result['score'] if result['label'] == 'positive' 
                              else -result['score'] if result['label'] == 'negative'
                              else 0,
                    'classification': label_map[result['label']]
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing text: {str(e)}")
            return {'compound': 0, 'classification': 'neutral'}

    def analyze_ticker(self, ticker):
        """
        Analyze sentiment for a specific stock ticker across all available dates.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            pandas.DataFrame: Daily sentiment scores for the ticker
        """
        # Load all posts for ticker
        posts_df = pd.DataFrame()
        ticker_path = os.path.join(self.data_root, ticker)
        
        if not os.path.exists(ticker_path):
            self.logger.warning(f"No data found for ticker {ticker}")
            return pd.DataFrame()
            
        # Find all RedditPosts.json files
        for root, dirs, files in os.walk(ticker_path):
            if "RedditPosts.json" in files:
                json_path = os.path.join(root, "RedditPosts.json")
                df = self.load_posts_from_json(json_path)
                if not df.empty:
                    posts_df = pd.concat([posts_df, df], ignore_index=True)
        
        if posts_df.empty:
            self.logger.warning(f"No posts found for ticker {ticker}")
            return pd.DataFrame()
        
        # Group by date and calculate sentiment
        results = []
        for date, group in posts_df.groupby(posts_df['date'].dt.date):
            daily_sentiments = []
            pos_count = 0
            neg_count = 0
            
            # Analyze each post
            for _, row in group.iterrows():
                sentiment = self.analyze_text(row['full_text'])
                
                # Weight by post score and comments
                weight = 1.0 + np.log1p(row['post_score'] + row['comment_count'])
                
                if sentiment['classification'] == 'positive':
                    pos_count += weight
                elif sentiment['classification'] == 'negative':
                    neg_count += weight
                    
                daily_sentiments.append(sentiment['compound'] * weight)
            
            # Calculate weighted sentiment score
            sentiment_score = 0
            if pos_count + neg_count > 0:
                sentiment_score = ((pos_count - neg_count) / (pos_count + neg_count)) * 100
            
            results.append({
                'date': date,
                'ticker': ticker,
                'sentiment_score': sentiment_score,
                'avg_compound': np.mean(daily_sentiments) if daily_sentiments else 0,
                'total_posts': len(daily_sentiments),
                'positive_count': pos_count,
                'negative_count': neg_count,
                'weighted_sentiment': sentiment_score
            })
        
        return pd.DataFrame(results)
import pandas as pd
import numpy as np
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from datetime import datetime
import logging
import os

class StockSentimentAnalyzer:
    """
    A class to analyze sentiment of stock-related social media posts using multiple models
    and computing aggregate daily sentiment scores. Reads data from JSON files.
    """
    
    def __init__(self, model_type="vader", input_path="../Data/RedditPosts"):
        """
        Initialize the sentiment analyzer with specified model type.
        
        Args:
            model_type (str): Type of model to use ('vader' or 'finbert')
            input_path (str): Path to directory containing JSON files with Reddit posts
        """
        self.model_type = model_type
        self.input_path = input_path
        self.setup_logger()
        
        if model_type == "vader":
            self.analyzer = SentimentIntensityAnalyzer()
        elif model_type == "finbert":
            model_name = "ProsusAI/finbert"
            self.analyzer = pipeline("sentiment-analysis", model=model_name)
        else:
            raise ValueError("Unsupported model type. Use 'vader' or 'finbert'")
    
    def setup_logger(self):
        """Configure logging for the sentiment analyzer."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='sentiment_analysis.log'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_posts_from_json(self, ticker):
        """
        Load Reddit posts from JSON files for a specific ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            pandas.DataFrame: DataFrame containing posts
        """
        try:
            # Construct path to JSON file
            json_path = os.path.join(self.input_path, f"{ticker}_posts.json")
            
            # Check if file exists
            if not os.path.exists(json_path):
                self.logger.error(f"No JSON file found for ticker {ticker}")
                return pd.DataFrame()
            
            # Read JSON file
            with open(json_path, 'r') as file:
                posts_data = json.load(file)
            
            # Convert to DataFrame
            df = pd.DataFrame(posts_data)
            
            # Ensure required columns exist
            required_cols = ['created_utc', 'title', 'selftext']
            if not all(col in df.columns for col in required_cols):
                self.logger.error(f"Missing required columns in JSON data for {ticker}")
                return pd.DataFrame()
            
            # Combine title and selftext for analysis
            df['full_text'] = df['title'] + ' ' + df['selftext'].fillna('')
            
            # Convert timestamp to datetime
            df['date'] = pd.to_datetime(df['created_utc'], unit='s')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading JSON data for {ticker}: {str(e)}")
            return pd.DataFrame()

    def analyze_text(self, text):
        """
        Analyze sentiment of a single text post.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: Sentiment scores and classification
        """
        if not isinstance(text, str):
            return {'compound': 0, 'classification': 'neutral'}
            
        try:
            if self.model_type == "vader":
                scores = self.analyzer.polarity_scores(text)
                # Classify based on compound score
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
        Analyze sentiment for a specific stock ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            pandas.DataFrame: Daily sentiment scores for the ticker
        """
        # Load posts for ticker
        posts_df = self.load_posts_from_json(ticker)
        
        if posts_df.empty:
            self.logger.warning(f"No posts found for ticker {ticker}")
            return pd.DataFrame()
        
        # Group by date
        results = []
        for date, group in posts_df.groupby(posts_df['date'].dt.date):
            daily_sentiments = []
            pos_count = 0
            neg_count = 0
            
            # Analyze each post
            for _, row in group.iterrows():
                sentiment = self.analyze_text(row['full_text'])
                
                if sentiment['classification'] == 'positive':
                    pos_count += 1
                elif sentiment['classification'] == 'negative':
                    neg_count += 1
                    
                daily_sentiments.append(sentiment['compound'])
            
            # Calculate sentiment score
            if pos_count + neg_count > 0:
                sentiment_score = ((pos_count - neg_count) / (pos_count + neg_count)) * 100
            else:
                sentiment_score = 0
            
            results.append({
                'date': date,
                'ticker': ticker,
                'sentiment_score': sentiment_score,
                'avg_compound': np.mean(daily_sentiments) if daily_sentiments else 0,
                'total_posts': len(daily_sentiments),
                'positive_posts': pos_count,
                'negative_posts': neg_count,
                'neutral_posts': len(daily_sentiments) - (pos_count + neg_count)
            })
        
        # Save results to JSON
        output_df = pd.DataFrame(results)
        output_path = os.path.join(self.input_path, f"{ticker}_sentiment.json")
        output_df.to_json(output_path, orient='records', date_format='iso')
        
        return output_df

    def generate_trading_signals(self, sentiment_scores, threshold_high=50, threshold_low=-50):
        """
        Generate trading signals based on sentiment scores.
        
        Args:
            sentiment_scores (pandas.DataFrame): DataFrame with daily sentiment scores
            threshold_high (float): Upper threshold for buy signal
            threshold_low (float): Lower threshold for sell signal
            
        Returns:
            pandas.DataFrame: DataFrame with trading signals
        """
        signals = sentiment_scores.copy()
        signals['signal'] = 'hold'
        signals.loc[signals['sentiment_score'] >= threshold_high, 'signal'] = 'buy'
        signals.loc[signals['sentiment_score'] <= threshold_low, 'signal'] = 'sell'
        
        # Save signals to JSON
        output_path = os.path.join(self.input_path, f"trading_signals.json")
        signals.to_json(output_path, orient='records', date_format='iso')
        
        return signals

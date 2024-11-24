import os
import pandas as pd
from SentimentAnalyzer import StockSentimentAnalyzer
import matplotlib.pyplot as plt
from datetime import datetime

def analyze_live_data():
    """Run sentiment analysis on actual Reddit data"""
    # Initialize analyzers
    data_root = "../Data"  # Adjust this path to where your actual data is stored
    vader_analyzer = StockSentimentAnalyzer(model_type="vader", data_root=data_root)
    
    # Get list of ticker folders
    ticker_folders = [f for f in os.listdir(data_root) 
                     if os.path.isdir(os.path.join(data_root, f)) and f.isupper()]
    
    print(f"Found {len(ticker_folders)} ticker folders: {ticker_folders}")
    
    results = {}
    for ticker in ticker_folders:
        print(f"\nAnalyzing {ticker}...")
        
        try:
            # Analyze ticker
            ticker_results = vader_analyzer.analyze_ticker(ticker)
            
            if not ticker_results.empty:
                results[ticker] = ticker_results
                
                # Print summary statistics
                print(f"\nResults for {ticker}:")
                print(f"Total Days Analyzed: {len(ticker_results)}")
                print(f"Average Sentiment Score: {ticker_results['sentiment_score'].mean():.2f}")
                print(f"Total Posts Analyzed: {ticker_results['total_posts'].sum()}")
                print(f"Most Positive Day: {ticker_results.loc[ticker_results['sentiment_score'].idxmax(), 'date']} "
                      f"(Score: {ticker_results['sentiment_score'].max():.2f})")
                print(f"Most Negative Day: {ticker_results.loc[ticker_results['sentiment_score'].idxmin(), 'date']} "
                      f"(Score: {ticker_results['sentiment_score'].min():.2f})")
                
                # Save results to CSV
                output_dir = os.path.join(data_root, ticker, "sentiment_analysis")
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f"{ticker}_sentiment_analysis.csv")
                ticker_results.to_csv(output_file, index=False)
                print(f"Results saved to {output_file}")
                
                # Create visualization
                plt.figure(figsize=(12, 6))
                plt.plot(ticker_results['date'], ticker_results['sentiment_score'])
                plt.title(f'{ticker} Sentiment Analysis')
                plt.xlabel('Date')
                plt.ylabel('Sentiment Score')
                plt.grid(True)
                plt.xticks(rotation=45)
                
                # Save plot
                plot_file = os.path.join(output_dir, f"{ticker}_sentiment_plot.png")
                plt.savefig(plot_file, bbox_inches='tight')
                plt.close()
                print(f"Plot saved to {plot_file}")
                
            else:
                print(f"No results found for {ticker}")
                
        except Exception as e:
            print(f"Error analyzing {ticker}: {str(e)}")
            continue
    
    # Generate overall summary
    print("\nOverall Analysis Summary:")
    print("-" * 50)
    summary_data = []
    for ticker, df in results.items():
        summary_data.append({
            'Ticker': ticker,
            'Average Sentiment': df['sentiment_score'].mean(),
            'Total Posts': df['total_posts'].sum(),
            'Days Analyzed': len(df),
            'Latest Sentiment': df.iloc[-1]['sentiment_score'] if not df.empty else None
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('Average Sentiment', ascending=False)
    
    # Save overall summary
    summary_file = os.path.join(data_root, "sentiment_summary.csv")
    summary_df.to_csv(summary_file, index=False)
    print("\nOverall Summary:")
    print(summary_df.to_string(index=False))
    print(f"\nSummary saved to {summary_file}")

if __name__ == "__main__":
    print("Starting Live Sentiment Analysis...")
    analyze_live_data()
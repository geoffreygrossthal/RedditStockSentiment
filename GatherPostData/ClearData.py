import os
import json

def clear_reddit_post_data(base_dir):
    # Walk through the base directory (Data directory)
    for stock_ticker in os.listdir(base_dir):
        stock_ticker_path = os.path.join(base_dir, stock_ticker)
        
        # Ensure it's a directory for a specific stock ticker
        if os.path.isdir(stock_ticker_path):
            # Walk through each year folder
            for year_folder in os.listdir(stock_ticker_path):
                year_folder_path = os.path.join(stock_ticker_path, year_folder)
                
                # Ensure it's a directory for a specific year
                if os.path.isdir(year_folder_path):
                    # Walk through each month folder
                    for month_folder in os.listdir(year_folder_path):
                        month_folder_path = os.path.join(year_folder_path, month_folder)
                        
                        # Ensure it's a directory for a specific month
                        if os.path.isdir(month_folder_path):
                            # Walk through each day folder
                            for day_folder in os.listdir(month_folder_path):
                                day_folder_path = os.path.join(month_folder_path, day_folder)
                                
                                # Check if the RedditPosts.json file exists in the day folder
                                file_path = os.path.join(day_folder_path, "RedditPosts.json")
                                if os.path.exists(file_path):
                                    # Clear the content of RedditPosts.json
                                    with open(file_path, 'w', encoding='utf-8') as f:
                                        json.dump([], f, ensure_ascii=False, indent=4)
                                    print(f"Cleared data in {file_path}")

def main():
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'Data')  # Path to the base Data directory
    clear_reddit_post_data(base_dir)

# Run the script
if __name__ == "__main__":
    main()

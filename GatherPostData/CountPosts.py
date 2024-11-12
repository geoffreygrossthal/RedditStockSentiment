import os
import json

# Function to count the total number of Reddit posts in the folder structure
def count_total_posts(base_dir):
    total_posts = 0
    # Walk through the directory structure
    for root, dirs, files in os.walk(base_dir):
        # Only look for JSON files named "RedditPosts.json"
        if "RedditPosts.json" in files:
            file_path = os.path.join(root, "RedditPosts.json")
            try:
                # Open and load the JSON data
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_posts += len(data)  # Add the number of posts in this file
            except json.JSONDecodeError:
                print(f"Error reading JSON file: {file_path}")
            except Exception as e:
                print(f"An error occurred: {e}")
    
    return total_posts

# Example usage
if __name__ == "__main__":
    # Set the base directory where your data is stored (where 'Data' folder is located)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data'))
    
    # Call the count_total_posts function
    total_posts = count_total_posts(base_dir)
    
    # Output the total number of posts
    print(f"Total number of Reddit posts: {total_posts}")

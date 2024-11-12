import os
import json

# Function to count the total number of Reddit posts in the folder structure
def count_total_posts(base_dir):
    total_posts = 0
    for root, dirs, files in os.walk(base_dir):
        if "RedditPosts.json" in files:
            file_path = os.path.join(root, "RedditPosts.json")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_posts += len(data)
            except json.JSONDecodeError:
                print(f"Error reading JSON file: {file_path}")
            except Exception as e:
                print(f"An error occurred: {e}")
    
    return total_posts

# Example usage
if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data'))
    total_posts = count_total_posts(base_dir)
    print(f"Total number of Reddit posts: {total_posts}")

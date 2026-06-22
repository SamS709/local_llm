import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

def get_markdown_urls(base_url):
    """
    Retrieve all URLs of Markdown files from a GitHub repository's content directory.
    
    Args:
        base_url (str): The base URL pointing to a GitHub content directory
        
    Returns:
        list: A list of URLs to all .md files in the subdirectories
    """
    # Parse the base URL
    parsed_url = urlparse(base_url)
    
    # Ensure we're working with the correct GitHub URL format
    if not parsed_url.netloc == 'github.com':
        raise ValueError("URL must be a GitHub URL")
    
    # Extract repository information from the path
    path_parts = parsed_url.path.strip('/').split('/')
    
    # Handle both blob and tree URLs
    owner = path_parts[0]
    repo = path_parts[1]
    
    # Determine if it's a blob or tree URL
    if len(path_parts) >= 4 and path_parts[2] == 'blob':
        branch = path_parts[3]
        base_path = '/'.join(path_parts[4:])
        # Convert blob URL to tree URL for API calls
        tree_url = f"https://github.com/{owner}/{repo}/tree/{branch}/{base_path}"
    elif len(path_parts) >= 4 and path_parts[2] == 'tree':
        branch = path_parts[3]
        base_path = '/'.join(path_parts[4:])
        tree_url = base_url
    else:
        # If it's just a repo URL without blob/tree, use default branch
        branch = 'main'  # Default to main branch
        base_path = '/'.join(path_parts[2:]) if len(path_parts) > 2 else ''
        tree_url = f"https://github.com/{owner}/{repo}/tree/{branch}/{base_path}"
    
    # GitHub API URL for directory listing
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{base_path}?ref={branch}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        contents = response.json()
        
        markdown_urls = []
        
        # Process each item in the directory
        for item in contents:
            if item['type'] == 'dir':
                # If it's a directory, recursively get its contents
                subdir_url = f"https://github.com/{owner}/{repo}/tree/{branch}/{item['path']}"
                sub_urls = get_markdown_urls(subdir_url)
                markdown_urls.extend(sub_urls)
            elif item['type'] == 'file' and item['name'].endswith('.md'):
                # If it's a Markdown file, add its GitHub URL to the list
                markdown_urls.append(item['html_url'])
        
        return markdown_urls
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from GitHub API: {e}")
        return []
    except Exception as e:
        print(f"Error processing directory contents: {e}")
        return []

def get_markdown_urls_from_github_tree(base_url):
    """
    Alternative approach using GitHub tree page scraping.
    
    Args:
        base_url (str): The GitHub tree URL
        
    Returns:
        list: A list of URLs to all .md files in the subdirectories
    """
    try:
        # Get the raw HTML content of the GitHub tree page
        response = requests.get(base_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        markdown_urls = []
        
        # Find all links that lead to Markdown files
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Check if the link points to a .md file
            if href.endswith('.md') and 'blob' in href:
                # Construct full URL
                full_url = urljoin(base_url, href)
                markdown_urls.append(full_url)
                
        return markdown_urls
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from GitHub: {e}")
        return []
    except Exception as e:
        print(f"Error processing GitHub tree page: {e}")
        return []

# Example usage
if __name__ == "__main__":
    # Example usage with the Hugo docs
    example_url = "https://github.com/gohugoio/hugoDocs/blob/master/content"
    urls = get_markdown_urls(example_url)
    print(f"Found {len(urls)} Markdown files:")
    for url in urls[:5]:  # Print first 5 URLs as example
        print(url)

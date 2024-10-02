import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin, urlparse

def create_directory_for_file(file_path):
    # Check and create necessary directories for the file path
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_static_file(file_url, base_dir):
    # Determine the local file path
    parsed_url = urlparse(file_url)
    local_path = os.path.join(base_dir, parsed_url.path.lstrip('/'))  # Remove the leading slash
    create_directory_for_file(local_path)  # Create necessary directories
    try:
        # Download the file
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        else:
            print(f"Error downloading {file_url}")
    except Exception as e:
        print(f"Error downloading {file_url}: {e}")

def download_template(url):
    base_dir = 'downloaded_template'
    # Create a directory to store the files
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    # Initial request to the website
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Initial request error. Status: {response.status_code}")
        return

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links to static files (CSS, JS, images)
    static_files = []
    for tag in soup.find_all(['link', 'script', 'img']):
        if tag.name == 'link' and tag.get('href'):
            static_files.append(urljoin(url, tag['href']))
        elif tag.name == 'script' and tag.get('src'):
            static_files.append(urljoin(url, tag['src']))
        elif tag.name == 'img' and tag.get('src'):
            static_files.append(urljoin(url, tag['src']))

    # Download the static files while maintaining paths and showing progress
    for file_url in tqdm(static_files, desc="Downloading files"):
        download_static_file(file_url, base_dir)

    # Save the HTML file
    html_filename = os.path.join(base_dir, 'index.html')
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print("Template download completed.")

if __name__ == '__main__':
    website_url = input("Please enter the website URL: ")
    download_template(website_url)

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def fetch_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        exit()

def save_to_file(directory, filename, content):
    try:
        with open(os.path.join(directory, filename), 'w', encoding='utf-8') as file:
            file.write(content)
    except IOError as e:
        print(f"Error saving the file {filename}: {e}")

def fetch_and_save_favicon(soup, base_url, directory):
    favicon = soup.find('link', rel=lambda value: value and 'icon' in value.lower())
    if favicon:
        favicon_url = urljoin(base_url, favicon.get('href'))
        try:
            favicon_content = requests.get(favicon_url).content
            with open(os.path.join(directory, 'favicon.ico'), 'wb') as file:
                file.write(favicon_content)
        except requests.RequestException as e:
            print(f"Error fetching favicon: {e}")

# Get the URL from the user
url = input("Enter the URL: ")

# Fetch the web page
web_content = fetch_url(url)

# Parse the web page
soup = BeautifulSoup(web_content, 'html.parser')

# Extract information
title = soup.title.string if soup.title else 'No Title'

# Extract meta description
meta_description = soup.find('meta', attrs={'name': 'description'})
description = meta_description.get('content') if meta_description else 'No Description Found'
description_line = f"Description: {description} - This site is used for {description}." if description != 'No Description Found' else f"Description: {description}."

# Extract keywords
meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
keywords = meta_keywords.get('content') if meta_keywords else 'No Keywords Found'

# Extract the first few paragraphs of text
paragraphs = '\n'.join([p.get_text() for p in soup.find_all('p')[:3]])

# Extract links
links = '\n'.join([urljoin(url, link.get('href')) for link in soup.find_all('a', href=True)])

# Extract images
images = '\n'.join([urljoin(url, img.get('src')) for img in soup.find_all('img', src=True)])

# Extract headings
headings = {}
for i in range(1, 7):
    tag = f'h{i}'
    headings[tag] = '\n'.join([h.get_text() for h in soup.find_all(tag)])

# Extract inline scripts
scripts = '\n'.join([script.get_text() for script in soup.find_all('script') if script.get_text()])

# Extract inline styles
styles = '\n'.join([style.get_text() for style in soup.find_all('style') if style.get_text()])

# Get the domain name for file naming
domain = urlparse(url).netloc.replace('.', '_')

# Create a directory to save files
directory = f"{domain}_data"
os.makedirs(directory, exist_ok=True)

# Save the extracted information to files
save_to_file(directory, f"{domain}-title.txt", title)
save_to_file(directory, f"{domain}-description.txt", description_line)
save_to_file(directory, f"{domain}-keywords.txt", keywords)
save_to_file(directory, f"{domain}-paragraphs.txt", paragraphs)
save_to_file(directory, f"{domain}-links.txt", links)
save_to_file(directory, f"{domain}-images.txt", images)

for tag, heading in headings.items():
    save_to_file(directory, f"{domain}-{tag}.txt", heading)

save_to_file(directory, f"{domain}-scripts.txt", scripts)
save_to_file(directory, f"{domain}-styles.txt", styles)

# Fetch and save favicon
fetch_and_save_favicon(soup, url, directory)

print(f"Data saved in folder: {directory}")

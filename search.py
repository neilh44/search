import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Function to scrape website content
def scrape_website(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text content from HTML
            text = " ".join([p.text for p in soup.find_all('p')])
            return text
        else:
            st.error(f"Failed to fetch website content. Error code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Function to extract links from a page
def extract_links(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and not href.startswith('#'):  # Filter out anchor links
                    absolute_url = urljoin(url, href)
                    links.append(absolute_url)
            return links
        else:
            st.error(f"Failed to fetch links from the page. Error code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"An error occurred while extracting links: {str(e)}")
        return []

# Function to crawl and index website
def crawl_and_index_website(url, max_depth=3):
    indexed_data = {}

    def crawl(url, depth):
        if depth > max_depth:
            return
        if url in indexed_data:
            return
        st.write(f"Crawling {url}...")
        text = scrape_website(url)
        if text:
            indexed_data[url] = text
            links = extract_links(url)
            for link in links:
                crawl(link, depth + 1)

    crawl(url, depth=1)
    return indexed_data

def main():
    st.title("Website Content Crawler & Indexer")

    # Input URL and max depth
    url = st.text_input("Enter website URL:")
    max_depth = st.slider("Maximum Depth (up to 5)", 1, 5, 3)

    if st.button("Crawl and Index"):
        if url:
            indexed_data = crawl_and_index_website(url, max_depth)
            if indexed_data:
                df = pd.DataFrame(list(indexed_data.items()), columns=["URL", "Text"])
                st.write("Indexed data:")
                st.write(df)
            else:
                st.error("Failed to crawl and index the website.")

if __name__ == "__main__":
    main()
    

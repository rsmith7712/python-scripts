#In Terminal: pip install requests
#In Terminal: pip install beautifulsoup4
#Find any and all items related to a company called Symetrix
#Makers of the absolute best equipment in the av space

import os
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import random
from config import SEARCH_TERMS, SEARCH_ENGINES, EBAY_SEARCH_URL, AMAZON_SEARCH_URLS

OUTPUT_DIR = r"C:\\Temp\\Results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.csv")
FAILED_URLS_LOG = os.path.join(OUTPUT_DIR, "failed_urls.log")
SEARCH_ENGINE_STATS_LOG = os.path.join(OUTPUT_DIR, "search_engine_stats.log")
LOCK = Lock()

search_engine_stats = {engine: {"success_count": 0, "failure_count": 0} for engine in SEARCH_ENGINES}

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Randomized headers
HEADERS = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
]

# Function to make requests with retries
def make_request(engine, url, retries=3, delay=5, timeout=10):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=random.choice(HEADERS), timeout=timeout)
            response.raise_for_status()
            with LOCK:
                search_engine_stats[engine]["success_count"] += 1
            return response
        except requests.RequestException:
            time.sleep(random.uniform(1, delay))
    with LOCK:
        search_engine_stats[engine]["failure_count"] += 1
    return None

# Function to search web pages using search engines
def search_web(term):
    search_results = []
    for engine in SEARCH_ENGINES:
        search_url = f"{engine}{term}"
        response = make_request(engine, search_url)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith("http"):
                    search_results.append(href)
    return search_results

# Function to save results to CSV
def save_results(results):
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Site", "URL", "Product Item", "Clickable URL"])
        for result in results:
            site, url, term = result
            clickable_url = f'=HYPERLINK("{url}", "{url}")'
            writer.writerow([site, url, term, clickable_url])

# Worker function to handle each search term
def process_term(term):
    search_results = search_web(term)
    return [["Unknown Site", url, term] for url in search_results]

# Main script execution
def main():
    all_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_term, term): term for category in SEARCH_TERMS for term in category.terms}
        for future in as_completed(futures):
            try:
                all_results.extend(future.result())
            except Exception as e:
                print(f"Error: {e}")
    save_results(all_results)
    print("Results saved to", OUTPUT_FILE)

if __name__ == "__main__":
    main()

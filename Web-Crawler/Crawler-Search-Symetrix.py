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

# Define constants
SEARCH_TERMS = [
    "Symetrix", "Symetrix, Inc.", "Symetrix Audio", "Symetrix Audio Inc.",
    "Jupiter", "SymVue", "Composer", "Zone Mix 761", "Server D100", "Prism", "Edge", "Radius", "Radius NX",
    "xIO Audio Expanders", "xIO XLR", "xIO Bluetooth", "xIO USB", "W-Series Remotes", "T-Series", "ARC Wall Panels",
    "xControl External Control Expander", "Control Server", "ARC-WEB"
]
OUTPUT_DIR = r"C:\\Temp\\Results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.csv")
SEARCH_ENGINES = [
    "https://www.google.com/search?q=",
    "https://www.bing.com/search?q=",
    "https://search.yahoo.com/search?p=",
    "https://duckduckgo.com/?q=",
    "https://www.baidu.com/s?wd=",
    "https://www.yandex.com/search/?text=",
    "https://www.ask.com/",
    "https://search.brave.com/",
    "https://www.dogpile.com/",
    "https://www.ecosia.org/",
    "https://www.elastic.co/elasticsearch",
    "https://www.excite.com/",
    "https://www.hotbot.com/",
    "https://kagi.com/",
    "https://www.lycos.com/",
    "https://www.metacrawler.com/",
    "https://www.mojeek.com/",
    "https://www.opensearch.org/",
    "https://www.qwant.com/",
    "https://www.sogou.com/",
    "https://www.startpage.com/",
    "https://swisscows.com/en",
    "https://you.com/",
    "https://search.yahoo.com/",
    "https://yacy.net/",
    "https://www.webcrawler.com/",
    "https://openverse.org/",
    "https://www.shodan.io/",
    "https://sepiasearch.org/",
    "https://www.google.com/shopping?udm=28",
    "https://www.bing.com/shop"
]
EBAY_SEARCH_URL = "https://www.ebay.com/sch/i.html?_nkw="
AMAZON_SEARCH_URLS = [
    "https://www.amazon.com/s?k=",
    "https://www.amazon.co.uk/s?k=",
    "https://www.amazon.ca?s?k=",
    "https://www.amazon.de?s?k=",
    "https://www.amazon.fr?s?k=",
    "https://www.amazon.co.jp?s?k=",
    "https://www.amazon.com.au?s?k=",
    "https://www.amazon.com.br?s?k=",
    "https://www.amazon.eg?s?k=",
    "https://www.amazon.it?s?k=",
    "https://www.amazon.ae?s?k=",
    "https://www.amazon.nl?s?k=",
    "https://www.amazon.pl?s?k=",
    "https://www.amazon.sa?s?k=",
    "https://www.amazon.sg?s?k=",
    "https://www.amazon.es?s?k="
]
FAILED_URLS_LOG = os.path.join(OUTPUT_DIR, "failed_urls.log")
LOCK = Lock()

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Function to make requests with retries
def make_request(url, headers, retries=3, delay=5, timeout=10):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed for URL: {url} with error: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    with LOCK:
        with open(FAILED_URLS_LOG, "a") as log_file:
            log_file.write(f"Failed URL: {url}\n")
    print(f"Skipping URL after {retries} attempts: {url}")
    return None

# Function to search web pages using search engines
def search_web(term):
    search_results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    for engine in SEARCH_ENGINES:
        search_url = f"{engine}{term}"
        response = make_request(search_url, headers)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and "url?q=" in href:
                    actual_url = href.split("url?q=")[1].split("&")[0]
                    search_results.append(actual_url)
    return search_results

# Function to search eBay
def search_ebay(term):
    search_results = []
    search_url = f"{EBAY_SEARCH_URL}{term}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    response = make_request(search_url, headers)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.select("li.s-item a.s-item__link"):
            href = item.get('href')
            if href:
                search_results.append(href)
    return search_results

# Function to search Amazon
def search_amazon(term):
    search_results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    for amazon_url in AMAZON_SEARCH_URLS:
        search_url = f"{amazon_url}{term}"
        response = make_request(search_url, headers)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.select("div.s-main-slot div.sg-col-4-of-12 a.a-link-normal"):
                href = item.get('href')
                if href:
                    search_results.append(urljoin(amazon_url, href))
    return search_results

# Function to save results to CSV
def save_results(results):
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Site", "URL", "Product Item", "Product URL"])
        for result in results:
            writer.writerow(result)

# Worker function to handle each search term
def process_term(term):
    print(f"Processing term: {term}")
    results = search_web(term) + search_ebay(term) + search_amazon(term)
    return [["Unknown Site", url, term, url] for url in results]

# Main script execution
def main():
    all_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_term = {executor.submit(process_term, term): term for term in SEARCH_TERMS}
        for future in as_completed(future_to_term):
            term = future_to_term[future]
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as e:
                print(f"Error processing term {term}: {e}")
    save_results(all_results)
    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

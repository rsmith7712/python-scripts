#In Terminal: pip install requests
#In Terminal: pip install beautifulsoup4

import os
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
    "https://www.yandex.com/search/?text="
]
EBAY_SEARCH_URL = "https://www.ebay.com/sch/i.html?_nkw="
AMAZON_SEARCH_URLS = [
    "https://www.amazon.com/s?k=",
    "https://www.amazon.co.uk/s?k=",
    "https://www.amazon.ca/s?k=",
    "https://www.amazon.de/s?k=",
    "https://www.amazon.fr/s?k=",
    "https://www.amazon.co.jp/s?k="
]

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Function to search web pages using search engines
def search_web(term):
    search_results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    for engine in SEARCH_ENGINES:
        search_url = f"{engine}{term}"
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and "url?q=" in href:
                    actual_url = href.split("url?q=")[1].split("&")[0]
                    search_results.append(actual_url)
        except requests.RequestException as e:
            print(f"Error fetching search results from {engine} for term '{term}': {e}")
    return search_results

# Function to search eBay
def search_ebay(term):
    search_results = []
    search_url = f"{EBAY_SEARCH_URL}{term}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.select("li.s-item a.s-item__link"):
            href = item.get('href')
            if href:
                search_results.append(href)
    except requests.RequestException as e:
        print(f"Error fetching eBay results for term '{term}': {e}")
    return search_results

# Function to search Amazon
def search_amazon(term):
    search_results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    for amazon_url in AMAZON_SEARCH_URLS:
        search_url = f"{amazon_url}{term}"
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.select("div.s-main-slot div.sg-col-4-of-12 a.a-link-normal"):
                href = item.get('href')
                if href:
                    search_results.append(urljoin(amazon_url, href))
        except requests.RequestException as e:
            print(f"Error fetching Amazon results from {amazon_url} for term '{term}': {e}")
    return search_results

# Function to save results to CSV
def save_results(results):
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Site", "URL", "Product Item", "Product URL"])
        for result in results:
            writer.writerow(result)

# Main script execution
def main():
    all_results = []
    for term in SEARCH_TERMS:
        print(f"Searching for term: {term}")
        results = search_web(term) + search_ebay(term) + search_amazon(term)
        for url in results:
            all_results.append(["Unknown Site", url, term, url])
    save_results(all_results)
    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

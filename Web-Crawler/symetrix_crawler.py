#In Terminal: pip install requests
#In Terminal: pip install beautifulsoup4
#In Terminal: pip install aiohttp
#Find any and all items related to a company called Symetrix
#Makers of the absolute best equipment in the av space

import os
import csv
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random
from threading import Lock
from config import SEARCH_TERMS, SEARCH_ENGINES, EBAY_SEARCH_URL, AMAZON_SEARCH_URLS

OUTPUT_DIR = r"C:\\Temp\\Results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.csv")
FAILED_URLS_LOG = os.path.join(OUTPUT_DIR, "failed_urls.log")
SEARCH_ENGINE_STATS_LOG = os.path.join(OUTPUT_DIR, "search_engine_stats.log")
LOCK = Lock()

HEADERS = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
]

search_engine_stats = {engine: {"success_count": 0, "failure_count": 0} for engine in SEARCH_ENGINES}

os.makedirs(OUTPUT_DIR, exist_ok=True)

async def fetch_url(session, engine, url):
    try:
        async with session.get(url, headers=random.choice(HEADERS), timeout=10) as response:
            if response.status == 200:
                with LOCK:
                    search_engine_stats[engine]["success_count"] += 1
                return await response.text()
            else:
                with LOCK:
                    search_engine_stats[engine]["failure_count"] += 1
                return None
    except Exception as e:
        with LOCK:
            search_engine_stats[engine]["failure_count"] += 1
        return None

async def search_web(term, session):
    search_results = []
    for engine in SEARCH_ENGINES:
        search_url = f"{engine}{term}"
        html = await fetch_url(session, engine, search_url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith("http"):
                    search_results.append(href)
    return search_results

def save_results(results):
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Site", "URL", "Product Item", "Clickable URL"])
        for result in results:
            site, url, term = result
            clickable_url = f'=HYPERLINK("{url}", "{url}")'
            writer.writerow([site, url, term, clickable_url])

async def process_term(term):
    async with aiohttp.ClientSession() as session:
        search_results = await search_web(term, session)
        return [["Unknown Site", url, term] for url in search_results]

async def main():
    all_results = []
    tasks = []
    for category in SEARCH_TERMS:
        for term in category.terms:
            tasks.append(process_term(term))
    results = await asyncio.gather(*tasks)
    for result in results:
        all_results.extend(result)
    save_results(all_results)
    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
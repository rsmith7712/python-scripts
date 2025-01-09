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
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
]

search_engine_stats = {engine: {"success_count": 0, "failure_count": 0} for engine in SEARCH_ENGINES}

os.makedirs(OUTPUT_DIR, exist_ok=True)

async def fetch_url(session, engine, url, retries=3):
    for attempt in range(retries):
        try:
            # Dynamically initialize stats for new engines or URLs
            with LOCK:
                if engine not in search_engine_stats:
                    search_engine_stats[engine] = {"success_count": 0, "failure_count": 0}
            
            await asyncio.sleep(random.uniform(0.5, 1.5))  # Reduced delay
            async with session.get(url, headers=random.choice(HEADERS), timeout=10) as response:
                if response.status == 200:
                    with LOCK:
                        search_engine_stats[engine]["success_count"] += 1
                    return await response.text()
                else:
                    with LOCK:
                        search_engine_stats[engine]["failure_count"] += 1
                    return None
        except ConnectionResetError:
            print(f"Connection reset by host for URL: {url}")
            with LOCK:
                search_engine_stats[engine]["failure_count"] += 1
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
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
            for link in soup.select('a[href]'):  # Optimized parsing
                href = link['href']
                if (
                    href.startswith("http") and 
                    "www.symetrix.co" not in href and 
                    "www.symetrixinc.com" not in href and 
                    "advertising" not in href and 
                    "affiliate-program" not in href and 
                    "aboutamazon" not in href and 
                    "affiliate" not in href
                ):
                    search_results.append(href)
    return search_results

async def search_resellers(term, session):
    reseller_results = []
    for search_url in AMAZON_SEARCH_URLS + [EBAY_SEARCH_URL]:
        url = f"{search_url}{term}"
        html = await fetch_url(session, search_url, url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for item in soup.select('a[href]'):  # Optimized parsing
                href = item['href']
                if (
                    href.startswith("http") and 
                    "www.symetrix.co" not in href and 
                    "www.symetrixinc.com" not in href and 
                    "advertising" not in href and 
                    "affiliate-program" not in href and 
                    "aboutamazon" not in href and 
                    "affiliate" not in href
                ):
                    reseller_results.append(href)
    return reseller_results

def save_results(results):
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "URL", "Search Term", "Clickable URL"])
        for result in results:
            source, url, term = result
            clickable_url = f'=HYPERLINK("{url}", "{url}")'
            writer.writerow([source, url, term, clickable_url])

async def process_term(term, session):
    web_results = await search_web(term, session)
    reseller_results = await search_resellers(term, session)
    combined_results = [["Web", url, term] for url in web_results] + [["Reseller", url, term] for url in reseller_results]
    return combined_results

async def main():
    all_results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for category in SEARCH_TERMS:
            for term in category.terms:
                tasks.append(process_term(term, session))

        results = []
        for chunk in [tasks[i:i + 20] for i in range(0, len(tasks), 20)]:  # Increased concurrency
            chunk_results = await asyncio.gather(*chunk)
            results.extend(chunk_results)

        for result in results:
            all_results.extend(result)
        save_results(all_results)
        print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())

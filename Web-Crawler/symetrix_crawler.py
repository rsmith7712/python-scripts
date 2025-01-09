#In Terminal: pip install requests
#In Terminal: pip install beautifulsoup4
#In Terminal: pip install aiohttp
#Find any and all items related to a company called Symetrix
#Makers of the absolute best equipment in the av space

import os  # Provides functions to interact with the operating system, such as file and directory manipulation
import csv  # Enables reading from and writing to CSV files
import aiohttp  # Asynchronous HTTP requests for fetching web content
import asyncio  # Allows asynchronous programming and task management
from bs4 import BeautifulSoup  # HTML and XML parsing library for extracting data from web pages
from urllib.parse import urljoin  # Utility for joining URLs to handle relative and absolute paths
import random  # Generates random numbers, used here for adding delays
from threading import Lock  # Ensures thread-safe access to shared resources
from config import SEARCH_TERMS, SEARCH_ENGINES, EBAY_SEARCH_URL, AMAZON_SEARCH_URLS  # Imports configuration constants

# Define output directory and files
OUTPUT_DIR = r"C:\\Temp\\Results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.csv")
FAILED_URLS_LOG = os.path.join(OUTPUT_DIR, "failed_urls.log")
SEARCH_ENGINE_STATS_LOG = os.path.join(OUTPUT_DIR, "search_engine_stats.log")
LOCK = Lock()

# Define headers to mimic browser behavior and avoid bot detection
HEADERS = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
]

# Initialize search engine stats for tracking success and failure counts
search_engine_stats = {engine: {"success_count": 0, "failure_count": 0} for engine in SEARCH_ENGINES}

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def fetch_url(session, engine, url, retries=3):
    """
    Fetch the content of a URL with retry logic.

    Args:
        session (ClientSession): The aiohttp session.
        engine (str): The search engine or URL being accessed.
        url (str): The URL to fetch.
        retries (int): Number of retries allowed.

    Returns:
        str or None: The HTML content of the URL or None if failed.
    """
    for attempt in range(retries):
        try:
            # Initialize stats for new URLs dynamically
            with LOCK:
                if engine not in search_engine_stats:
                    search_engine_stats[engine] = {"success_count": 0, "failure_count": 0}

            # Add a random delay to prevent rate-limiting
            await asyncio.sleep(random.uniform(0.5, 1.5))
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
    """
    Perform a search for a term on all configured search engines.

    Args:
        term (str): The search term.
        session (ClientSession): The aiohttp session.

    Returns:
        list: List of URLs found during the search.
    """
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
    """
    Search reseller platforms for a term.

    Args:
        term (str): The search term.
        session (ClientSession): The aiohttp session.

    Returns:
        list: List of reseller URLs found.
    """
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
    """
    Save the collected results to a CSV file.

    Args:
        results (list): The list of results to save.
    """
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "URL", "Search Term", "Clickable URL"])
        for result in results:
            source, url, term = result
            clickable_url = f'=HYPERLINK("{url}", "{url}")'
            writer.writerow([source, url, term, clickable_url])

async def process_term(term, session):
    """
    Process a single search term by querying both web and reseller platforms.

    Args:
        term (str): The search term.
        session (ClientSession): The aiohttp session.

    Returns:
        list: Combined results from web and reseller searches.
    """
    web_results = await search_web(term, session)
    reseller_results = await search_resellers(term, session)
    combined_results = [["Web", url, term] for url in web_results] + [["Reseller", url, term] for url in reseller_results]
    return combined_results

async def main():
    """
    Main function to coordinate the web crawling process.
    """
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

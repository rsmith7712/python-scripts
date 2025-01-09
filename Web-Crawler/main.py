#In Terminal: pip install requests
#In Terminal: pip install beautifulsoup4
#In Terminal: pip install aiohttp
#In Terminal: pip install psutil
#Find any and all items related to a company called Symetrix
#Makers of the absolute best equipment in the av space

import os  # Provides functions to interact with the operating system, such as file and directory manipulation
import aiohttp  # Asynchronous HTTP requests for fetching web content
import asyncio  # Allows asynchronous programming and task scheduling
from config import SEARCH_TERMS, SEARCH_ENGINES, EBAY_SEARCH_URL, AMAZON_SEARCH_URLS  # Imports configuration constants for search terms and URLs
from utils import log_resource_usage, fetch_url, parse_html, save_results_to_csv  # Reusable utility functions for resource monitoring, URL fetching, HTML parsing, and saving results

# Define constants
OUTPUT_DIR = r"C:\\Temp\\Results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.csv")
HEADERS = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
]
EXCLUDE_TERMS = ["www.symetrix.co", "www.symetrixinc.com", "advertising", "affiliate-program", "aboutamazon", "affiliate"]

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def process_search(term, session):
    """
    Process a single search term across all search engines and resellers.

    Args:
        term (str): The search term.
        session (ClientSession): The aiohttp session.

    Returns:
        list: Combined results from web and reseller searches.
    """
    results = []
    for engine in SEARCH_ENGINES:
        search_url = f"{engine}{term}"
        html = await fetch_url(session, engine, search_url, HEADERS)
        if html:
            links = await parse_html(html, EXCLUDE_TERMS)
            results.extend([["Web", link, term] for link in links])

    for reseller_url in AMAZON_SEARCH_URLS + [EBAY_SEARCH_URL]:
        search_url = f"{reseller_url}{term}"
        html = await fetch_url(session, reseller_url, search_url, HEADERS)
        if html:
            links = await parse_html(html, EXCLUDE_TERMS)
            results.extend([["Reseller", link, term] for link in links])

    return results

async def main():
    """
    Main function to coordinate the web crawling process.
    """
    all_results = []
    async with aiohttp.ClientSession() as session:
        # Start resource monitoring
        monitor_task = asyncio.create_task(log_resource_usage())

        tasks = [process_search(term, session) for category in SEARCH_TERMS for term in category.terms]

        # Process tasks with concurrency limit
        for chunk in [tasks[i:i + 40] for i in range(0, len(tasks), 40)]:
            chunk_results = await asyncio.gather(*chunk)
            for result in chunk_results:
                all_results.extend(result)

        # Stop resource monitoring
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

    # Save results to file
    save_results_to_csv(all_results, OUTPUT_FILE)
    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())

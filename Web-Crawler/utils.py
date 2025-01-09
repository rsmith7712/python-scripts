import csv  # Enables reading from and writing to CSV files
import random  # Provides functionality to generate random numbers, used here for delays
import asyncio  # Allows asynchronous programming and task scheduling
import psutil  # Provides utilities to monitor system resource usage
from bs4 import BeautifulSoup  # HTML and XML parsing library for extracting data from web pages
from threading import Lock  # Ensures thread-safe operations for shared resources

# Define lock for thread-safe operations
LOCK = Lock()

async def log_resource_usage():
    """
    Periodically log system resource usage.
    """
    while True:
        process = psutil.Process()
        mem_info = process.memory_info()
        print(f"CPU Usage: {psutil.cpu_percent()}%")
        print(f"Memory Usage: {mem_info.rss / (1024 * 1024):.2f} MB")
        await asyncio.sleep(5)  # Log every 5 seconds

async def fetch_url(session, engine, url, headers, retries=3):
    """
    Fetch the content of a URL with retry logic.

    Args:
        session (ClientSession): The aiohttp session.
        engine (str): The search engine or URL being accessed.
        url (str): The URL to fetch.
        headers (list): List of headers for the request.
        retries (int): Number of retries allowed.

    Returns:
        str or None: The HTML content of the URL or None if failed.
    """
    for attempt in range(retries):
        try:
            await asyncio.sleep(random.uniform(0.5, 1.5))  # Randomized delay
            async with session.get(url, headers=random.choice(headers), timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return None
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                return None

async def parse_html(html, exclude_terms):
    """
    Parse HTML and extract valid links.

    Args:
        html (str): HTML content to parse.
        exclude_terms (list): Terms to exclude from links.

    Returns:
        list: List of valid links.
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.select('a[href]'):
        href = link['href']
        if href.startswith("http") and not any(term in href for term in exclude_terms):
            links.append(href)
    return links

def save_results_to_csv(results, output_file):
    """
    Save results to a CSV file.

    Args:
        results (list): List of results to save.
        output_file (str): Path to the output CSV file.
    """
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "URL", "Search Term", "Clickable URL"])
        for result in results:
            source, url, term = result
            clickable_url = f'=HYPERLINK("{url}", "{url}")'
            writer.writerow([source, url, term, clickable_url])

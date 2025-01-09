
import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random

# to store the URLs discovered to visit
# in a specific order
urls = queue.PriorityQueue()
# high priority
urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))

# to store the pages already visited
visited_urls = []

# until all pages have been visited
while not urls.empty():
    # get the page to visit from the list
    _, current_url = urls.get()

    # crawling logic
    response = requests.get(current_url)
    soup = BeautifulSoup(response.content, "html.parser")

    visited_urls.append(current_url)

    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        url = link_element['href']

        # if the URL is relative to scrapingcourse.com or
        # any of its subdomains
        if re.match(r"https://(?:.*\.)?scrapingcourse\.com", url):
            # if the URL discovered is new
            if url not in visited_urls and url not in [item[1] for item in urls.queue]:
                # low priority
                priority_score = 1
                # if it is a pagination page
                if re.match(r"^https://scrapingcourse\.com/ecommerce/page/\d+/?$", url):
                    # high priority
                    priority_score = 0.5
                urls.put((priority_score, url))

    # pause the script for a random delay
    # between 1 and 3 seconds
    time.sleep(random.uniform(1, 3)) 

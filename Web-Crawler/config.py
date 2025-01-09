from dataclasses import dataclass  # Allows creation of simple classes to store data
from typing import List  # Provides type hinting for lists

@dataclass
class SearchCategory:
    """
    Represents a category of search terms.

    Attributes:
        name (str): The name of the category.
        terms (List[str]): List of search terms under the category.
    """
    name: str
    terms: List[str]

# Search terms grouped by category
SEARCH_TERMS = [
    SearchCategory("GENERAL", [
        "Symetrix", "Symetrix, Inc.", "Symetrix Audio", "Symetrix SymNet"
    ]),
    SearchCategory("SOFTWARE_SITE_DESIGN", [
        "Symetrix Composer", "Symetrix Jupiter Software", "Symetrix Zone Mix 761 Software"
    ]),
    SearchCategory("SOFTWARE_UTILITY", [
        "Symetrix Audio Inc.", "Symetrix SymVue"
    ]),
    SearchCategory("DIGITAL_SIGNAL_PROCESSORS_OPEN", [
        "Symetrix DSP", "Symetrix Edge", "Symetrix Prism", "Symetrix Radius", "Symetrix Radius NX",
        "Symetrix Radius and Edge Expansion Cards", "Symetrix Server D100", "Symetrix Solus NX"
    ]),
    SearchCategory("DIGITAL_SIGNAL_PROCESSORS_FIXED", [
        "Symetrix Jupiter", "Symetrix Zone Mix 761"
    ]),
    SearchCategory("ENDPOINTS", [
        "Symetrix xIO Audio Expanders", "Symetrix xIO Audio Expander xln 4", "Symetrix xIO Audio Expander xln 12",
        "Symetrix xIO Audio Expander xOut 4", "Symetrix xIO Audio Expander xOut 12", "Symetrix xIO Audio Expander xIO 4x4",
        "Symetrix xIO Audio Expander xIO Stage 4x4", "Symetrix xIO Bluetooth xIO Bluetooth",
        "Symetrix xIO Bluetooth xIO Bluetooth RCA-3.5", "Symetrix xIO USB", "Symetrix xIO USB xIO USB",
        "Symetrix xIO XLR", "Symetrix xIO XLR xIO XLR 1×1", "Symetrix xIO XLR xIn XLR 2", "Symetrix xIO XLR xIO XLR 2×2",
        "Symetrix xIO XLR xIn XLR 4"
    ]),
    SearchCategory("SYSTEM_CONTROL", [
        "Symetrix ARC Wall Panels", "Symetrix ARC Wall Panel ARC-3", "Symetrix ARC Wall Panel ARC-2e",
        "Symetrix ARC Wall Panel ARC-K1e", "Symetrix ARC Wall Panel ARC-SW4e", "Symetrix ARC Wall Panel ARC-EX4e",
        "Symetrix ARC Wall Panel RC-3", "Symetrix ARC Wall Panel ARC-PSe", "Symetrix ARC-WEB",
        "Symetrix Control Server", "Symetrix T-Series", "Symetrix T-Series Touchscreen T-5 Glass",
        "Symetrix T-Series Touchscreen T-7 Glass", "Symetrix T-Series Touchscreen T-10 Glass",
        "Symetrix W-Series", "Symetrix W-Series Remotes W1", "Symetrix W-Series Remotes W2",
        "Symetrix W-Series Remotes W3", "Symetrix W-Series Remotes W4", "Symetrix xControl External Control Expander",
        "Symetrix xControl External Control Expander xControl"
    ])
]

# Search engines for web scraping
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

# eBay search URL
EBAY_SEARCH_URL = "https://www.ebay.com/sch/i.html?_nkw="

# Amazon search URLs
AMAZON_SEARCH_URLS = [
    "https://www.amazon.com/s?k=",
    "https://www.amazon.co.uk?s=k",
    "https://www.amazon.ca?s=k",
    "https://www.amazon.de?s=k",
    "https://www.amazon.fr?s=k",
    "https://www.amazon.co.jp?s=k",
    "https://www.amazon.com.au?s=k",
    "https://www.amazon.com.br?s=k",
    "https://www.amazon.eg?s=k",
    "https://www.amazon.it?s=k",
    "https://www.amazon.ae?s=k",
    "https://www.amazon.nl?s=k",
    "https://www.amazon.pl?s=k",
    "https://www.amazon.sa?s=k",
    "https://www.amazon.sg?s=k",
    "https://www.amazon.es?s=k"
]

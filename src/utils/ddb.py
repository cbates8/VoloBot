"""General D&D Beyond Scraping Utils"""

from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0"
HTML_PARSER = "html.parser"

BASE_URL = "https://www.dndbeyond.com"
SPELL_URL = BASE_URL + "/spells/{spell_name}"


def get_ddb_page(url: str) -> BeautifulSoup:
    """Get parsed HTML of a ddb webpage

    Args:
        url (`str`): URL of the page to parse

    Returns:
        `BeautifulSoup`: Parsed HTML as BeautifulSoup object
    """
    req = Request(url, headers={"User-Agent": USER_AGENT})
    # Open the url and parse the HTML
    with urlopen(req) as spell_page:
        # Parse the site's HTML using the Beautiful Soup web-scraping library
        parsed_html = BeautifulSoup(spell_page, HTML_PARSER)

    return parsed_html


def get_ddb_statblock_value(item_name: str, parsed_html: BeautifulSoup) -> str:
    """
    Extract all text from a ddb-statblock-item

    Args:
        item_name (`str`): Name of the statblock-item to scrape
        parsed_html (`BeautifulSoup`): HTML of the site containing the statblocks

    Returns:
        `str`: Scraped text from ddb
    """
    # Identify the item containing the information we want
    item = parsed_html.find("div", class_=f"ddb-statblock-item ddb-statblock-item-{item_name}")

    # Get all text containied in the value section of the statblock
    return item.find("div", class_="ddb-statblock-item-value").get_text(";", True).split(";")[0]  # pyright: ignore[reportOptionalMemberAccess]

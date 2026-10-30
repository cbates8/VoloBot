"""Spell Scraping Utils"""

from urllib.error import HTTPError

from bs4 import BeautifulSoup
from discord import Embed

from constants.paths import SPELLS_PATH
from utils.ddb import SPELL_URL, get_ddb_page, get_ddb_statblock_value
from utils.embed import dict_to_embed
from utils.json_utils import read_json_async

# Dict containing categories of spell information.
# Keys are the pretty title to be used in the Embed,
# values are the name of the HTML object to scrape
SPELL_ATTRIBUTES = {
    "Level": "level",
    "Casting Time": "casting-time",
    "Range": "range-area",
    "Components": "components",
    "Duration": "duration",
    "School": "school",
    "Attack/Save": "attack-save",
    "Damage Type": "damage-effect",
}
LOCAL_SOURCES = ["all", "local"]
ONLINE_SOURCES = ["all", "web"]
VALID_SOURCES = ["all", "local", "web"]
MISSING_SPELL_TEXT = "**Error:** Cannot find spell '{spell_name}'"


def get_spell_name(parsed_html: BeautifulSoup) -> str:
    """Extract teh spell name from the page title

    Args:
        parsed_html (`BeautifulSoup`): Spell page parsed HTML

    Returns:
        `str`: Spell name
    """
    # Get the name of the spell from the page title
    return parsed_html.find("h1", class_="page-title").text  # pyright: ignore[reportOptionalMemberAccess]


def get_spell_description(parsed_html: BeautifulSoup) -> str:
    """Extract the spell description from the page content

    Args:
        parsed_html (`BeautifulSoup`): Spell page parsed HTML

    Returns:
        `str`: Spell description
    """
    # Get the spell description from the page content
    return parsed_html.find("div", class_="more-info-content").get_text("\n\n", True)  # pyright: ignore[reportOptionalMemberAccess]


def get_spell_from_ddb(spell_name: str) -> Embed:
    """Scrape spell info from DnD Beyond (https://www.dndbeyond.com/spells/{spell-name})

    Args:
        spell_name (`str`): Name of the spell to lookup

    Returns:
        `Embed`: Discord embed containing spell info
    """
    spell_name = spell_name.replace(" ", "-")
    url = SPELL_URL.format(spell_name=spell_name)
    parsed_html = get_ddb_page(url)

    # Extract basic spell information
    spell_name = get_spell_name(parsed_html)
    spell_description = get_spell_description(parsed_html)

    # Create a dict to store spell information. Will be turned into an Embed later
    spell_dict = {"description": spell_description}

    # Scrape each spell attribute and add to the dictionary
    for label, item in SPELL_ATTRIBUTES.items():
        spell_dict[label] = get_ddb_statblock_value(item, parsed_html)

    # Add ddb page url to the dictonary
    spell_dict["Source"] = url

    return dict_to_embed(spell_name, spell_dict)


async def get_spell_from_file(spell_name: str) -> Embed | None:
    """Get spell info from local JSON file

    Args:
        spell_name (`str`): Name of the spell to lookup

    Returns:
        `Embed`: Discord embed containing spell info
    """
    # Search local spell file for information
    known_spells = await read_json_async(SPELLS_PATH)

    for name, description in known_spells.items():
        if spell_name.lower() == name.lower():
            embed = dict_to_embed(name, description)
            return embed


async def get_spell(spell_name: str, source: str = "all") -> str | Embed:
    """Get a spell from a local file or online

    Args:
        spell_name (`str`): Name of the spell to lookup
        source (`str`): Source to check. Defaults to 'all'

    Returns:
        `Union[str, Embed]`: Spell as a Discord embed, or an error message
    """
    response = None

    # Validate source
    source = source.lower()
    if source not in VALID_SOURCES:
        return f"**Error:** Invalid Source '{source}'\nMust be one of: `{' | '.join(VALID_SOURCES)}`"

    # Check for the spell online (via ddb)
    if source in ONLINE_SOURCES:
        try:
            response = get_spell_from_ddb(spell_name)
        except HTTPError:
            if source == "web":
                response = MISSING_SPELL_TEXT.format(spell_name=spell_name)

        # If we have a non-null response, we can return
        # If not, source must be 'all' so we will check local file
        if response:
            return response

    # Check for the spell locally
    if source in LOCAL_SOURCES:
        response = await get_spell_from_file(spell_name)

    if not response:
        response = MISSING_SPELL_TEXT.format(spell_name=spell_name)
    return response

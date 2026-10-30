"""Rule Lookup Utils"""

from discord import Embed

from constants.paths import RULES_PATH
from utils.embed import dict_to_embed
from utils.json_utils import read_json_async


def get_known_rules(rulebook: dict[str, str]) -> Embed:
    """Get list of known rules

    Args:
        rulebook (`dict`): Dict containing rules

    Returns:
        `Embed`: Discord embed representing known rules
    """
    title = "Known Rules"
    content = {"content": [rule for rule in rulebook.keys()]}

    return dict_to_embed(title, content)


async def get_rule(rule: str | None = None) -> Embed | None:
    """Return entry of the specified rule
    If no rule provided, return list of known rules

    Args:
        rule (`str`, optional): The rule item to list. Defaults to `None`.

    Returns:
        `Embed` | `None`: Discord embed representing rule content
    """
    rulebook = await read_json_async(RULES_PATH)

    # If no item specified, return list of known rules
    if not rule:
        return get_known_rules(rulebook)

    # If an entry exists for this rule, create an embed
    rule = rule.title()
    if entry := rulebook.get(rule):
        return dict_to_embed(rule, entry)

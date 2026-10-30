"""Discord Embed Utils"""

from discord import Embed
from typing import Any


def dict_to_embed(title: str, content: dict[str, Any]) -> Embed:  # pyright: ignore[reportExplicitAny]
    """Convert a dict object to a Discord Embed object

    Args:
        title (`str`): Title of the Embed
        content (`dict`): Content of the Embed

    Returns:
        `Embed`: Discord Embed object
    """
    embed = Embed(title=title)
    for key, value in content.items():
        if key == "Description":
            embed.description = value
        elif key == "Content" and isinstance(value, list):
            formatted_values = ""
            for line in value:  # pyright: ignore[reportUnknownVariableType]
                formatted_values += f"{line}\n\n"
            embed.description = formatted_values
        else:
            if isinstance(value, dict):
                formatted_values = ""
                for k, v in value.items():  # pyright: ignore[reportUnknownVariableType]
                    formatted_values += f"{k}: {v}\n\n"
            else:
                formatted_values = value
            embed.add_field(name=key, value=formatted_values, inline=False)
    return embed


def create_error_embed(error: Exception, multiline: bool = False) -> Embed:
    """Create a Discord Embed describing a Python Exception

    Args:
        error (`Exception`): An error encountered by the program
        multiline (`bool`): If error text should be a single or multi-line codeblock

    Returns:
        `Embed`: A Discord embed object with a description of the error, as well as traceback
    """
    embed = Embed(title="I've encountered an error:")
    val = f"```{error}```" if multiline else f"`{error}`"
    embed.add_field(
        name=type(error).__name__,
        value=val,
        inline=False,
    )
    return embed

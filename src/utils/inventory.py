"""Inventory Management Utils"""

from discord import Embed

from constants.paths import INVENTORY_PATH
from utils.embed import dict_to_embed
from utils.json_utils import read_json_async, write_json_async


async def get_item(item: str | None = None) -> Embed | None:
    """Get content of the inventory.

    Return entry of the specified item.
    If no item provided, return content of full inventory

    Args:
        item (`str`, optional): The inventory item to list. Defaults to `None`.

    Returns:
        `Embed` | `None`: Discord embed representing inventory content
    """
    inventory = await read_json_async(INVENTORY_PATH)

    # If no item specified, return entire inventory
    if not item:
        return dict_to_embed("Inventory", inventory)

    # If an entry exists for this item, create an embed
    if entry := inventory.get(item):
        return dict_to_embed(item, entry)


async def store_item(item: str, quantity: int = 1, description: str | None = None) -> None:
    """Store an item in inventory

    Args:
        item (`str`): Item to add
        quantity (`int`): Quantity of items to remove. Defaults to `1`.
        description (`str`): Description of item. Defaults to `None`.
    """
    # Read inventory from disk
    inventory = await read_json_async(INVENTORY_PATH)

    # Check if the item already exists in inventory
    # If so, increase the quantity
    if item in inventory.keys():
        inventory[item]["quantity"] += quantity
        # Update the description of the item if given
        if description is not None:
            inventory[item]["description"] = description
    # Otherwise, simply add the item to the dict
    else:
        inventory[item] = {"description": description, "quantity": quantity}

    # Save inventory
    await write_json_async(INVENTORY_PATH, inventory)


async def remove_item(item: str, quantity: int | None = None) -> None:
    """Remove an item from inventory

    Args:
        item (`str`): Item to remove
        quantity (`int`): Quantity of items to remove. If `None`, removes all. Defaults to `None`.
    """
    # Read inventory from disk
    inventory = await read_json_async(INVENTORY_PATH)

    if quantity is None or quantity >= inventory[item]["quantity"]:
        del inventory[item]
    else:
        inventory[item]["quantity"] -= quantity

    # Save inventory
    await write_json_async(INVENTORY_PATH, inventory)

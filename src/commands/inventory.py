"""Inventory Commands"""

from discord.ext.commands import Bot, Cog, Context, command, parameter

from utils.inventory import get_item, remove_item, store_item


class Inventory(Cog):
    """Cog defining commands related to inventory management"""

    def __init__(self: "Inventory", bot: Bot) -> None:
        """Init Cog

        Args:
            bot (`Bot`): Discord Bot object
        """
        self.bot: Bot = bot

    @command(name="bag", help="Check the party's inventory")
    async def check_inventory(
        self: "Inventory",
        ctx: Context[Bot],
        item: str | None = parameter(
            default=None,
            description=" The name of the inventory item to list. If ommitted, entire inventory will be listed",
        ),
    ) -> None:
        """Displays the contents of inventory.json

        Args:
            ctx (`Context`): Message context object from Discord
            item (`str`, optional): The name of the inventory item to list. If ommitted, entire inventory will be listed. Defaults to `None`.
        """
        if embed := await get_item(item):
            await ctx.send(embed=embed)
        else:
            response = f"Could not find item '{item}' in your inventory."
            await ctx.send(response)

    @command(name="store", help="Store items in the party's inventory")
    async def store_inventory(
        self: "Inventory",
        ctx: Context[Bot],
        item: str = parameter(description="The name of the item to store"),
        quantity: int = parameter(default=1, description="The quantity of the item to store"),
        description: str | None = parameter(default=None, description="A description of the stored item"),
    ) -> None:
        """Store items in inventory (write to inventory.json)

        Args:
            ctx (`Context`): Message context object from Discord
            item (`str`): The name of the item to store
            quantity (`int`, optional): The quantity of the item to store. Defaults to '1'.
            description (`str`, optional): A description of the stored item. Defaults to `None`.
        """
        await store_item(item, quantity, description)

        response = f"Added {quantity} {item} to your inventory."

        await ctx.send(response)

    @command(name="remove", help="Remove items from the party's inventory")
    async def remove_inventory(
        self: "Inventory",
        ctx: Context[Bot],
        item: str = parameter(description="The name of the item to remove"),
        quantity: int | None = parameter(default=None, description="The quantity of the item to remove"),
    ) -> None:
        """Remove items from inventory.json

        Args:
            ctx (`Context`): Message context object from Discord
            item (`str`): Item to remove from the inventory
            quantity (`int`, optional): The quantity of items to remove. Defaults to `None` (Removes all items).
        """
        await remove_item(item, quantity)

        response = f"Removed {'all' if quantity is None else quantity} {item} from your inventory."

        await ctx.send(response)


async def setup(bot: Bot) -> None:
    """Setup Cog

    Args:
        bot (`Bot`): Discord Bot object
    """
    await bot.add_cog(Inventory(bot))

"""Critical Hit/Miss Commands"""

from discord.ext.commands import Bot, Cog, Context, command, parameter

from utils.crit import get_crit_result, get_fumble_result


class Crit(Cog):
    """Cog defining commands related to critical hits and misses"""

    def __init__(self: "Crit", bot: Bot) -> None:
        """Init Cog

        Args:
            bot (`Bot`): Discord Bot object
        """
        self.bot: Bot = bot

    @command(name="crit", help="Search the critical hit table")
    async def send_crit_outcome(
        self: "Crit",
        ctx: Context[Bot],
        crit_percentage: int = parameter(description="Percentage representing critical hit severity"),
        dmg_type: str = parameter(description="Type of damage being inflicted"),
    ) -> None:
        """Search the provided csv of the crititcal hit table using the user's inputed percentage and damage type. Reply with the resulting effect

        Args:
            ctx (`Context`): Message context object from Discord
            crit_percentage (`int`): Percentage representing critical hit severity
            dmg_type (`str`): Type of damage being inflicted
        """
        response = await get_crit_result(crit_percentage, dmg_type)
        await ctx.send(response)

    @command(name="fumble", help="Search the critical miss table")
    async def send_fumble_outcome(
        self: "Crit",
        ctx: Context[Bot],
        fumble_percentage: int = parameter(description="Percentage representing critical miss severity"),
    ) -> None:
        """Search the provided csv of the crititcal miss table using the user's inputed percentage. Reply with the resulting effect

        Args:
            ctx (`Context`): Message context object from Discord
            fumble_percentage (`int`): Percentage representing critical miss severity
        """
        response = await get_fumble_result(fumble_percentage)
        await ctx.send(response)


async def setup(bot: Bot) -> None:
    """Setup Cog

    Args:
        bot (`Bot`): Discord Bot object
    """
    await bot.add_cog(Crit(bot))

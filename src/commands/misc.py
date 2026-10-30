"""Misc Commands"""

import os
import random

from discord import Embed, File
from discord.ext.commands import Bot, Cog, Context, command, parameter

from constants.paths import MEME_DIR


class Misc(Cog):
    """Cog defining miscellaneous commands that don't quite fit in any other category"""

    def __init__(self: "Misc", bot: Bot) -> None:
        """Init Cog

        Args:
            bot (`Bot`): Discord Bot object
        """
        self.bot: Bot = bot

    @command(name="roll", help="Roll virtual dice")
    async def roll_dice(
        self: "Misc",
        ctx: Context[Bot],
        number_of_dice: int = parameter(description="The number of dice to be rolled"),
        number_of_sides: int = parameter(description="How many sides each rolled die should have"),
    ) -> None:
        """Simulate rolling of dice

        Args:
            ctx (`Context`): Message context object from Discord
            number_of_dice (`int`): The number of dice to be rolled
            number_of_sides (`int`): How many sides each rolled die should have
        """
        # Chooses a random int between 1 and the given number of sides
        # Repeats as many times as number_of_dice
        dice = [str(random.choice(range(1, number_of_sides + 1))) for _ in range(number_of_dice)]
        await ctx.send(", ".join(dice))

    @command(name="meme", help="Dank Me Me")
    async def send_meme(self: "Misc", ctx: Context[Bot]) -> None:
        """Sends a meme to context

        Args:
            ctx (`Context`): Message context object from Discord
        """
        meme_candidates = os.listdir(MEME_DIR)  # Get all files from the "memes" folder
        random_meme = random.choice(meme_candidates)  # Choose a random file
        # If .DS_Store is selected at random, continue choosing until the selected file is NOT .DS_Store
        while random_meme == ".DS_Store":
            random_meme = random.choice(meme_candidates)
        await ctx.send(file=File(f"{MEME_DIR}/{random_meme}"))

    @command(name="ping", help="Ping Volobot")
    async def send_ping(self: "Misc", ctx: Context[Bot]) -> None:
        """Send the estimated ping of the requesting user

        Args:
            ctx (`Context`): Message context object from Discord
        """
        embed = Embed(title="Pong!")
        response = await ctx.send(embed=embed)
        # Calculate the time difference between ping request and pong response
        ping = (response.created_at - ctx.message.created_at).total_seconds() * 1000
        embed.add_field(name=":ping_pong:", value=f"{int(ping)} ms")  # Add calculated ping to the embed
        await response.edit(embed=embed)  # edit response to include calculated ping (ms)


async def setup(bot: Bot) -> None:
    """Setup Cog

    Args:
        bot (`Bot`): Discord Bot object
    """
    await bot.add_cog(Misc(bot))

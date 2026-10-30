"""Bot Events"""

import os
import random

from discord import Game, Message
from discord.ext.commands import Bot, Cog, Context

from constants.quotes import QUOTES
from utils.embed import create_error_embed
from utils.logging import get_logger

LOGGER = get_logger(os.path.basename(__file__))


class Event(Cog):
    """Cog defining bot events"""

    def __init__(self: "Event", bot: Bot) -> None:
        """Init Cog

        Args:
            bot (`Bot`): Discord Bot object
        """
        self.bot: Bot = bot

    @Cog.listener()
    async def on_ready(self: "Event") -> None:
        """On ready, bot will log to the console confirming its connection to discord, as well as any guilds it has been added to"""
        if not self.bot.user:
            # I'm not sure this is even possible but it makes the type checker happy
            LOGGER.error("ERROR: Bot is not logged in")
            return

        LOGGER.info("%s has connected to Discord!", self.bot.user.name)
        LOGGER.info("%s is connected to the following guilds:", self.bot.user.name)
        for guild in self.bot.guilds:
            LOGGER.info("\t- %s (id: %s)", guild.name, guild.id)
        # set activity status to "Playing Dungeons and Dragons"
        await self.bot.change_presence(activity=Game(name="Dungeons and Dragons"))

    @Cog.listener()
    async def on_message(self: "Event", message: Message) -> None:
        """When seeing a message containing 'volo', the bot will reply with a random quote

        Args:
            message (`Message`): A Message object from Discord
        """
        # checks if the bot was the one to send the message. If so, breaks out of function to avoid a continuous reply to itself
        if message.author == self.bot.user:
            return
        # If any version of the string 'volo' appears in a message, choose a random quote and send it to the channel
        if "volo" in message.content.lower():
            response = random.choice(QUOTES)
            await message.channel.send(response)

    @Cog.listener()
    async def on_command_error(self: "Event", ctx: Context[Bot], error: Exception) -> None:
        """Send error messages to context in addition to logging

        Args:
            ctx (`Context`): Message context object from Discord
            error (`Exception`): The error encountered in the program. This will likely be a UserInputError (i.e. BadArgument), or some other unhandled error
        """
        LOGGER.exception(error, exc_info=error)
        embed = create_error_embed(error)
        await ctx.send(embed=embed)


async def setup(bot: Bot) -> None:
    """Setup Cog

    Args:
        bot (`Bot`): Discord Bot object
    """
    await bot.add_cog(Event(bot))

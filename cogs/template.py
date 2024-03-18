from discord.ext import commands
from discord.ext.commands import Context

class Timers(commands.Cog, name="Timers"):
    def __init__(self, bot) -> None:
        self.bot = bot


async def setup(bot) -> None:
    await bot.add_cog(Timers(bot))
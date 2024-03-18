from discord.ext import commands
from discord.ext.commands import Context

class Help(commands.Cog, name="help", aliases=["h"]):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.excluded_cogs = ["YouTubeNotifier", "TwitchNotifier", "Timers"]

    @commands.command()
    async def help(self, ctx: Context):
        """
        Displays help message for all loaded cogs and their commands.
        """
        help_message = "```"
        for cog in self.bot.cogs.values():
            if cog.qualified_name not in self.excluded_cogs:
                help_message += f"\n== {cog.qualified_name} ==\n"
                for command in cog.get_commands():
                    if not command.hidden:
                        help_message += f"{command.name}: {command.help}\n"
        help_message += "```"
        await ctx.send(help_message)

async def setup(bot) -> None:
    await bot.add_cog(Help(bot))
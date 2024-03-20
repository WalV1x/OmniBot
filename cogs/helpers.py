import json
import os

import discord
from discord.ext import commands

HELP_JSON_PATH = 'json/help.json'


# ------------------------ COGS ------------------------ #

class Help(commands.Cog, name="Help"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # ------------------------ COGS ------------------------ #

    @commands.Cog.listener()
    async def on_ready(self):
        """Event listener called when the cog is loaded."""
        print(f"{self.__class__.__name__} cog has been loaded.")

    async def import_data_from_json(self, json_path: str) -> dict:
        """
        Import help data from a JSON file.

        Args:
            json_path (str): Path to the JSON file.

        Returns:
            dict: Help data.
        """
        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"JSON file '{json_path}' not found.")
        with open(json_path, 'r') as file:
            data = json.load(file)
        return data

    @commands.command(name="help", aliases=["h"])
    async def help_command(self, ctx):
        """Command to display help information."""
        try:
            data = await self.import_data_from_json(HELP_JSON_PATH)
            for embed_data in data.get('embeds', []):
                embed = discord.Embed.from_dict(embed_data)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred while fetching help data: {e}")


async def setup(bot) -> None:
    """Function to setup the Help cog."""
    await bot.add_cog(Help(bot))

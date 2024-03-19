from discord.ext import commands
from discord.ext.commands import Context
import discord
import json


class Help(commands.Cog, name="help"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded.")

    async def import_data_from_json(self):
        with open('json/help.json', 'r') as file:
            data = json.load(file)
        return data

    @commands.command(name="help", aliases=["h"])
    async def help_command(self, ctx):
        data = await self.import_data_from_json()
        for embed_data in data['embeds']:
            embed = discord.Embed.from_dict(embed_data)
            await ctx.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Help(bot))
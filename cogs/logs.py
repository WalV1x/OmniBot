import json
import re

import discord
from discord.ext import commands

with open('config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)


class Logs(commands.Cog, name="Logs"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.log_channel_id = config_data['log_channel']

    def load_config(self):
        return config_data

    def write_config(self, config):
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

    async def send_log_embed(self, content, icon_url=None):
        if self.log_channel_id:
            channel = self.bot.get_channel(self.log_channel_id)
            embed = discord.Embed(
                title="Log",
                description=content,
                color=0x3DD5FA
            )

            if icon_url:
                embed.set_footer(text="Omnibot - Logs Services",
                                 icon_url="https://raw.githubusercontent.com/WalV1x/OmniBot/main/img/logo.jpeg")

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.send_log_embed(f'{member.mention} has joined the server.', icon_url=self.bot.user.avatar_url)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.send_log_embed(f'{member.name} has left the server.', icon_url=self.bot.user.avatar_url)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await self.send_log_embed(f'A message from {message.author.name} was deleted: {message.content}', icon_url=self.bot.user.avatar_url)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.send_log_embed(
            f'A message from {before.author.name} was edited: {before.content} -> {after.content}', icon_url=self.bot.user.avatar_url)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        added_roles = set(after.roles) - set(before.roles)
        removed_roles = set(before.roles) - set(after.roles)
        if added_roles:
            await self.send_log_embed(
                f'{after.name} has been given the following roles: {", ".join([role.name for role in added_roles])}.')
        if removed_roles:
            await self.send_log_embed(
                f'{after.name} has had the following roles removed: {", ".join([role.name for role in removed_roles])}.')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        added_roles = set(after.roles) - set(before.roles)
        removed_roles = set(before.roles) - set(after.roles)
        if added_roles:
            await self.send_log_embed(
                f'{after.name} has been given the following roles: {", ".join([role.name for role in added_roles])}.')
        if removed_roles:
            await self.send_log_embed(
                f'{after.name} has had the following roles removed: {", ".join([role.name for role in removed_roles])}.')

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await self.send_log_embed(f'A new channel named {channel.name} has been created.')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await self.send_log_embed(f'The channel named {channel.name} has been deleted.')

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if before.name != after.name:
            await self.send_log_embed(f'The channel {before.name} has been renamed to {after.name}.')

    @commands.group(name="log", aliases=["Log", "logs", "Logs"],
                    brief="Log command")
    @commands.has_permissions(manage_messages=True)
    async def log(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="Log Commands", description="List of available log commands", color=0x00ff00)
            embed.add_field(name="🛠️ Setup", value="Setup the log channel", inline=False)
            embed.add_field(name="❌ Remove", value="Remove the log channel", inline=False)
            embed.set_footer(text="Omnibot - Logs Services",
                             icon_url="https://raw.githubusercontent.com/WalV1x/OmniBot/main/img/logo.jpeg")

            await ctx.send(embed=embed)
        else:
            await ctx.send_help(ctx.command)

    @log.command(name="setup", aliases=["Setup"],
                 brief="Setup the log channel")
    @commands.has_permissions(manage_messages=True)
    async def log_set(self, ctx, channel_mention: str):
        channel_id_match = re.match(r"<#(\d+)>", channel_mention)
        if channel_id_match:
            channel_id = int(channel_id_match.group(1))
            self.log_channel_id = channel_id
            await ctx.send(f"Log channel set to {channel_mention}")

            config_data = self.load_config()
            config_data['log_channel'] = channel_id
            self.write_config(config_data)
        else:
            await ctx.send("Invalid channel mention. Please mention a valid channel.")

    @log.command(name="remove", aliases=["Remove"],
                 brief="Remove the log channel")
    @commands.has_permissions(manage_messages=True)
    async def log_remove(self, ctx):
        config_data = self.load_config()
        if 'log_channel' in config_data:
            config_data['log_channel'] = None
            self.write_config(config_data)
            await ctx.send("Log channel removed.")
        else:
            await ctx.send("No log channel was set.")


async def setup(bot) -> None:
    await bot.add_cog(Logs(bot))

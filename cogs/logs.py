import json
import re

# Importez le contenu de config.json directement
with open('config.json', 'r') as f:
    config_data = json.load(f)

from discord.ext import commands


class Logs(commands.Cog, name="Logs"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.log_channel_id = config_data['log_channel']

    # Supprimez les décorateurs @staticmethod
    def load_config(self):
        return config_data

    def write_config(self, config):
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.log_message(f'{member.mention} has joined the server.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.log_message(f'{member.name} has left the server.')

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.log_message(f'{user.name} has been banned from the server.')

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await self.log_message(f'{user.name} has been unbanned from the server.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if before.channel is None:
                await self.log_message(f'{member.name} has joined voice channel {after.channel.name}.')
            elif after.channel is None:
                await self.log_message(f'{member.name} has left voice channel {before.channel.name}.')
            else:
                await self.log_message(f'{member.name} has moved from {before.channel.name} to {after.channel.name}.')

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await self.log_message(f'A message from {message.author.name} was deleted: {message.content}')

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        deleted_messages = '\n'.join([message.content for message in messages])
        await self.log_message(f'{len(messages)} messages were deleted:\n{deleted_messages}')

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.log_message(f'A message from {before.author.name} was edited: {before.content} -> {after.content}')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            added_roles = set(after.roles) - set(before.roles)
            removed_roles = set(before.roles) - set(after.roles)
            if added_roles:
                await self.log_message(
                    f'{after.name} has been given the following roles: {", ".join([role.name for role in added_roles])}.')
            if removed_roles:
                await self.log_message(
                    f'{after.name} has had the following roles removed: {", ".join([role.name for role in removed_roles])}.')

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await self.log_message(f'A new channel named {channel.name} has been created.')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await self.log_message(f'The channel named {channel.name} has been deleted.')

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if before.name != after.name:
            await self.log_message(f'The channel {before.name} has been renamed to {after.name}.')

    async def log_message(self, content):
        if self.log_channel_id:
            channel = self.bot.get_channel(self.log_channel_id)
            await channel.send(content)

    @commands.group(name="log")
    async def log(self, ctx):
        """
        Manage log channels.

        Subcommands:
        - set: Set the log channel.
        - remove: Remove the log channel.
        """
        pass

    @log.command(name="set", aliases=["s"])
    async def log_set(self, ctx, channel_mention: str):
        """
        Set the log channel.

        Args:
            channel_mention (str): The mention of the log channel ("<#channel_id>").
        """
        # Extraire l'ID du canal à partir de la mention
        channel_id_match = re.match(r"<#(\d+)>", channel_mention)
        if channel_id_match:
            channel_id = int(channel_id_match.group(1))
            self.log_channel_id = channel_id
            await ctx.send(f"Log channel set to {channel_mention}")

            # Charger la configuration actuelle
            config_data = self.load_config()
            # Mettre à jour la valeur du canal de journalisation dans la configuration
            config_data['log_channel'] = channel_id
            # Enregistrer la configuration mise à jour dans le fichier JSON
            self.write_config(config_data)
        else:
            await ctx.send("Invalid channel mention. Please mention a valid channel.")

    @log.command(name="remove", aliases=["r"])
    async def log_remove(self, ctx):
        """
        Remove the log channel.
        """
        config_data = self.load_config()
        if 'log_channel' in config_data:
            config_data['log_channel'] = None
            self.write_config(config_data)
            await ctx.send("Log channel removed.")
        else:
            await ctx.send("No log channel was set.")


async def setup(bot) -> None:
    await bot.add_cog(Logs(bot))

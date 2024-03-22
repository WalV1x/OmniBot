import json
import os

import discord
from discord.ext import commands

script_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(script_dir, "..", "config.json")


def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
        config["locked_channels"] = [int(channel_id) for channel_id in config.get("locked_channels", [])]
        return config


def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config["locked_channels"] = [int(channel_id) for channel_id in config.get("locked_channels", [])]
        json.dump(config, f, indent=4)


# ------------------------ COGS ------------------------ #

class manageChannel(commands.Cog, name="manageChannel"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.config = load_config()

        # ------------------------ COGS ------------------------ #

    @commands.group(name="channel",
                    brief="Manage the channel")
    @commands.has_permissions(manage_channels=True)
    async def Manage_channel(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Channel Management Commands",
                description="Here are the commands you can use to manage channels:",
                color=0x3DD5FA
            )

            embed.add_field(name="🔒 Lock", value="Lock a channel", inline=False)
            embed.add_field(name="🔓 Unlock", value="Unlock a channel", inline=False)
            embed.add_field(name="📋 Clone", value="Clone a channel", inline=False)
            embed.add_field(name="📊 Channel", value="Show channel statistics", inline=False)
            embed.add_field(name="⚙️ Modify", value="Modify channel settings", inline=False)
            embed.add_field(name="🗑️ Delete", value="Delete a channel", inline=False)
            embed.add_field(name="➕ Create", value="Create a channel", inline=False)
            embed.add_field(name="📝 List", value="List all channels", inline=False)
            embed.set_footer(text="Omnibot - Channel Management Services",
                             icon_url="https://raw.githubusercontent.com/WalV1x/OmniBot/main/img/logo.jpeg")

            await ctx.send(embed=embed)

    @Manage_channel.command(name="lock", aliases=["Lock"],
                            brief="Lock a channel")
    @commands.has_permissions(manage_channels=True)
    async def lock_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Locks the specified channel. If no channel is mentioned, the current channel will be locked.
        """
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is None or overwrite.send_messages is True:
            overwrite.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(f"The channel {channel.mention} has been locked successfully.")
            self.config["locked_channels"].append(channel.id)
            save_config(self.config)
        else:
            await ctx.send(f"The channel {channel.mention} is already locked.")

    @lock_channel.error
    async def lock_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to manage channels.")

    @Manage_channel.command(name="unlock", aliases=["Unlock"], brief="Unlock the channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Unlocks the specified channel. If no channel is mentioned, the current channel will be unlocked.
        """
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is False:
            overwrite.send_messages = None  # Setting to None allows the role to send messages
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(f"The channel {channel.mention} has been unlocked successfully.")
            # Remove the channel ID from the list of locked channels
            if channel.id in self.config["locked_channels"]:
                self.config["locked_channels"].remove(channel.id)
            save_config(self.config)
        else:
            await ctx.send(f"The channel {channel.mention} is already unlocked.")

    @Manage_channel.command(name="clone", aliases=["Clone"],
                            brief="Clone a channel")
    @commands.has_permissions(manage_channels=True)
    async def clone_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Clones the specified channel.
        """
        try:
            # Create a new channel with the same properties as the original channel
            new_channel = await channel.clone()
            await ctx.send(f"Channel {channel.mention} has been successfully cloned as {new_channel.mention}.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to clone channels.")
        except discord.HTTPException:
            await ctx.send("Failed to clone the channel. An error occurred.")

    @Manage_channel.command(name="stats", aliases=["Stats"],
                            brief="Shows channel statistics")
    @commands.has_permissions(manage_channels=True)
    async def stats(self, ctx, channel: discord.TextChannel = None):
        """
        Shows statistics about the usage of the specified channel. If no channel is mentioned,
        statistics for the current channel will be displayed.
        """
        channel = channel or ctx.channel
        channel_name = channel.name
        channel_mentions = channel.mention
        channel_messages = await channel.history(limit=None).flatten()
        total_messages = len(channel_messages)
        user_message_count = {}

        # Count messages per user
        for message in channel_messages:
            user_id = message.author.id
            user_message_count[user_id] = user_message_count.get(user_id, 0) + 1

        # Sort users by message count
        sorted_users = sorted(user_message_count.items(), key=lambda x: x[1], reverse=True)

        # Prepare statistics message
        stats_message = f"Statistics for {channel_mentions}:\n"
        stats_message += f"Total messages: {total_messages}\n\n"
        stats_message += "Top 5 users by message count:\n"
        for i, (user_id, message_count) in enumerate(sorted_users[:5], start=1):
            user = ctx.guild.get_member(user_id)
            user_name = user.display_name if user else f"Unknown User ({user_id})"
            stats_message += f"{i}. {user_name}: {message_count} messages\n"

        await ctx.send(stats_message)

    @Manage_channel.command(name="modify", aliases=["Modify"],
                            brief="Modify channel settings")
    @commands.has_permissions(manage_channels=True)
    async def modify_channel(self, ctx, channel: discord.TextChannel, *, settings: str):
        """
        Modify the settings of the specified channel. Example usage:
        !channel modify #channel-name name NewName
        !channel modify #channel-name topic NewTopic
        !channel modify #channel-name permission @RoleName send_messages False
        """
        settings_list = settings.split()

        if len(settings_list) < 2:
            await ctx.send("Invalid format. Please provide at least one setting to modify.")
            return

        setting_type = settings_list[0].lower()
        setting_value = ' '.join(settings_list[1:])

        if setting_type == "name":
            try:
                await channel.edit(name=setting_value)
                await ctx.send(f"Channel name has been successfully changed to `{setting_value}`.")
            except discord.Forbidden:
                await ctx.send("I don't have permission to modify channel name.")
            except discord.HTTPException:
                await ctx.send("Failed to modify channel name. An error occurred.")
        elif setting_type == "topic":
            try:
                await channel.edit(topic=setting_value)
                await ctx.send(f"Channel topic has been successfully changed to `{setting_value}`.")
            except discord.Forbidden:
                await ctx.send("I don't have permission to modify channel topic.")
            except discord.HTTPException:
                await ctx.send("Failed to modify channel topic. An error occurred.")
        elif setting_type == "permission":
            try:
                role_mention, permission_type, permission_value = setting_value.split()
                role = discord.utils.get(ctx.guild.roles, name=role_mention)
                if role:
                    permissions = channel.overwrites_for(role)
                    setattr(permissions, permission_type, permission_value.lower() == 'true')
                    await channel.set_permissions(role, overwrite=permissions)
                    await ctx.send(
                        f"Permission `{permission_type}` for role `{role_mention}` has been successfully changed to `{permission_value}`.")
                else:
                    await ctx.send("Role not found.")
            except ValueError:
                await ctx.send(
                    "Invalid format for permission modification. Please provide role mention, permission type, and permission value.")
            except discord.Forbidden:
                await ctx.send("I don't have permission to modify channel permissions.")
            except discord.HTTPException:
                await ctx.send("Failed to modify channel permissions. An error occurred.")
        else:
            await ctx.send("Invalid setting type. Please specify 'name', 'topic', or 'permission'.")

    @Manage_channel.command(name="delete", aliases=["Delete", "del"],
                            brief="Delete a channel")
    @commands.has_permissions(manage_channels=True)
    async def delete_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Deletes the specified channel.
        """
        try:
            await channel.delete()
            await ctx.send(f"Channel {channel.name} has been successfully deleted.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete channels.")
        except discord.HTTPException:
            await ctx.send("Failed to delete the channel. An error occurred.")

    @Manage_channel.command(name="create", aliases=["Create", "new", "New"],
                            brief="Create a channel")
    @commands.has_permissions(manage_channels=True)
    async def create_channel(self, ctx, channel_name: str, channel_type: str = "text"):
        """
        Create a new channel with the specified name and type (default: text).
        """
        try:
            if channel_type.lower() == "text":
                new_channel = await ctx.guild.create_text_channel(name=channel_name)
            elif channel_type.lower() == "voice":
                new_channel = await ctx.guild.create_voice_channel(name=channel_name)
            else:
                await ctx.send("Invalid channel type. Please specify 'text' or 'voice'.")
                return

            await ctx.send(f"Channel {new_channel.name} has been successfully created.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to create channels.")
        except discord.HTTPException:
            await ctx.send("Failed to create the channel. An error occurred.")

    @Manage_channel.command(name="list", aliases=["List"],
                            brief="List all channels")
    @commands.has_permissions(manage_channels=True)
    async def list_channels(self, ctx):
        """
        List all channels present on the Discord server.
        """
        channels = ctx.guild.channels
        text_channels = [channel.name for channel in channels if isinstance(channel, discord.TextChannel)]
        voice_channels = [channel.name for channel in channels if isinstance(channel, discord.VoiceChannel)]

        text_channels_str = "\n".join(text_channels)
        voice_channels_str = "\n".join(voice_channels)

        embed = discord.Embed(title="Channel List", color=discord.Color.blue())
        embed.add_field(name="Text Channels", value=text_channels_str or "No text channels", inline=True)
        embed.add_field(name="Voice Channels", value=voice_channels_str or "No voice channels", inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(manageChannel(bot))

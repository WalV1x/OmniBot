import discord
from discord.ext import commands
import json
import re

class SocialAlert(commands.Cog, name="SocialAlert"):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def read_config(self):
        with open("config.json", "r") as f:
            return json.load(f)

    async def write_config(self, config):
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

    async def extract_channel_id(self, channel_link: str) -> str:
        # Extract channel ID from YouTube link
        youtube_pattern = r'^https?://(?:www\.)?youtube\.com/channel/([a-zA-Z0-9_-]+)'
        youtube_match = re.match(youtube_pattern, channel_link)
        if youtube_match:
            return youtube_match.group(1)

        # Extract channel username from Twitch link
        twitch_pattern = r'^https?://(?:www\.)?twitch\.tv/(\w+)'
        twitch_match = re.match(twitch_pattern, channel_link)
        if twitch_match:
            return twitch_match.group(1)

        return None

    @commands.command(name="youtube")
    @commands.has_permissions(administrator=True)
    async def manage_youtube_channel(self, ctx: commands.Context, action: str, channel_arg: str = None):
        """
        Add, remove, or set the notification channel for YouTube.

        Parameters:
        - action (str): 'add', 'remove', or 'set'.
        - channel_arg (str): Either the ID or link of the YouTube channel.

        Example usage:
        - Add a YouTube channel:
          !youtube add youtube_channel_id_or_link
        - Remove a YouTube channel:
          !youtube remove youtube_channel_id_or_link
        - Set the notification channel for YouTube:
          !youtube set channel_name
        """
        # Command implementation goes here

        config = await self.read_config()

        if action.lower() == "list":
            monitored_channels = config.get('monitored_youtube_channels', [])
            if monitored_channels:
                await ctx.send("Monitored YouTube Channel IDs:")
                for channel_id in monitored_channels:
                    await ctx.send(channel_id)
            else:
                await ctx.send("No YouTube channels are being monitored.")
            return

        if not channel_arg:
            await ctx.send("Please provide the ID or link of the YouTube channel.")
            return

        if not channel_arg:
            await ctx.send("Please provide the ID or link of the YouTube channel.")
            return

        # Check if the provided argument is a link, if so, extract the channel ID
        if channel_arg.startswith("http"):
            channel_id = await self.extract_channel_id(channel_arg)
            if not channel_id:
                await ctx.send("Invalid YouTube channel link.")
                return
        else:
            channel_id = channel_arg

        if action.lower() == "add":
            if channel_id not in config['monitored_youtube_channels']:
                config['monitored_youtube_channels'].append(channel_id)
                await ctx.send(f"Channel with ID {channel_id} added to the list of monitored channels.")
            else:
                await ctx.send("This channel is already being monitored.")
        elif action.lower() == "remove":
            if channel_id in config['monitored_youtube_channels']:
                config['monitored_youtube_channels'].remove(channel_id)
                await ctx.send(f"Channel with ID {channel_id} removed from the list of monitored channels.")
            else:
                await ctx.send("This channel is not being monitored.")
        elif action.lower() == "set":
            config['youtube_notification_channel'] = channel_id
            await ctx.send(f"YouTube notification channel set to {channel_id}.")
        else:
            await ctx.send("Invalid action. Please use 'add', 'remove', 'set', or 'list'.")

        await self.write_config(config)

    @commands.command(name="twitch")
    @commands.has_permissions(administrator=True)
    async def manage_twitch_channel(self, ctx: commands.Context, action: str, channel_arg: str = None):
        """
        Add, remove, or set the notification channel for Twitch.

        Parameters:
        - action (str): 'add', 'remove', or 'set'.
        - channel_arg (str): Either the ID or link of the Twitch channel.

        Example usage:
        - Add a Twitch channel:
          !twitch add twitch_channel_id_or_link
        - Remove a Twitch channel:
          !twitch remove twitch_channel_id_or_link
        - Set the notification channel for Twitch:
          !twitch set channel_name
        """
        # Command implementation goes here

        config = await self.read_config()

        if action.lower() == "list":
            monitored_channels = config.get('monitored_twitch_channels', [])
            if monitored_channels:
                await ctx.send("Monitored Twitch Channel IDs:")
                for channel_id in monitored_channels:
                    await ctx.send(channel_id)
            else:
                await ctx.send("No Twitch channels are being monitored.")
            return

        if not channel_arg:
            await ctx.send("Please provide the ID or link of the Twitch channel.")
            return

        # Check if the provided argument is a link, if so, extract the channel ID
        if channel_arg.startswith("http"):
            # Implement logic to extract Twitch channel ID from the link if needed
            pass
        else:
            channel_id = channel_arg

        if action.lower() == "add":
            if channel_id not in config['monitored_twitch_channels']:
                config['monitored_twitch_channels'].append(channel_id)
                await ctx.send(f"Channel with ID {channel_id} added to the list of monitored Twitch channels.")
            else:
                await ctx.send("This channel is already being monitored.")
        elif action.lower() == "remove":
            if channel_id in config['monitored_twitch_channels']:
                config['monitored_twitch_channels'].remove(channel_id)
                await ctx.send(f"Channel with ID {channel_id} removed from the list of monitored Twitch channels.")
            else:
                await ctx.send("This channel is not being monitored.")
        elif action.lower() == "set":
            config['twitch_notification_channel'] = channel_id
            await ctx.send(f"Twitch notification channel set to {channel_id}.")
        else:
            await ctx.send("Invalid action. Please use 'add', 'remove', 'set', or 'list'.")

        await self.write_config(config)

async def setup(bot) -> None:
    await bot.add_cog(SocialAlert(bot))
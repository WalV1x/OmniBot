import json

import requests
from discord.ext import commands, tasks
from googleapiclient.discovery import build

# Load configuration from config.json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# YouTube API setup
youtube = build("youtube", "v3", developerKey=config["youtube_api_key"])


# ------------------------ COGS ------------------------ #

class YouTubeNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_new_videos.start()

    # ------------------------ COGS ------------------------ #

    def cog_unload(self):
        self.check_new_videos.cancel()

    async def get_new_videos(self):
        new_videos = []
        for channel_id in config.get("monitored_youtube_channels", []):
            request = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                order="date",
                maxResults=1  # Only fetch the latest video
            )
            response = request.execute()
            if "items" in response:
                new_videos.extend(response["items"])
        return new_videos

    @tasks.loop(minutes=30)  # Check for new videos every 30 minutes
    async def check_new_videos(self):
        new_videos = await self.get_new_videos()
        if new_videos:
            notification_channel_id = config.get("youtube_notification_channel")
            if notification_channel_id:
                channel = self.bot.get_channel(notification_channel_id)
                for video in new_videos:
                    video_title = video["snippet"]["title"]
                    video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                    await channel.send(f"New video: {video_title}\n{video_url}")


class TwitchNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_new_streams.start()

    def cog_unload(self):
        self.check_new_streams.cancel()

    async def get_new_streams(self):
        new_streams = []
        headers = {"Client-ID": config.get("twitch_client_id")}
        for channel_name in config.get("monitored_twitch_channels", []):
            response = requests.get(f"https://api.twitch.tv/helix/streams?user_login={channel_name}", headers=headers)
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                new_streams.extend(data["data"])
        return new_streams

    @tasks.loop(minutes=30)  # Check for new streams every 30 minutes
    async def check_new_streams(self):
        new_streams = await self.get_new_streams()
        if new_streams:
            notification_channel_id = config.get("twitch_notification_channel")
            if notification_channel_id:
                channel = self.bot.get_channel(notification_channel_id)
                for stream in new_streams:
                    stream_title = stream["title"]
                    stream_url = f"https://www.twitch.tv/{stream['user_name']}"
                    await channel.send(f"New stream: {stream_title}\n{stream_url}")


async def setup(bot) -> None:
    await bot.add_cog(YouTubeNotifier(bot))
    await bot.add_cog(TwitchNotifier(bot))

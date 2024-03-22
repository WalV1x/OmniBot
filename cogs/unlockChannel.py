import json
import discord
from discord.ext import commands
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(script_dir, "..", "config.json")

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
        config["locked_channels"] = [str(channel_id) for channel_id in config.get("locked_channels", [])]
        return config


def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config["locked_channels"] = [int(channel_id) for channel_id in config.get("locked_channels", [])]
        json.dump(config, f, indent=4)


# ------------------------ COGS ------------------------ #

class UnlockChannel(commands.Cog, name="UnlockChannel"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.config = load_config()

    # ------------------------ COGS ------------------------ #

    @commands.command(name="unlock", aliases=["unlockchannel"], brief="Unlock the channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Unlocks the specified channel. If no channel is mentioned, the current channel will be unlocked.
        """
        channel = channel or ctx.channel
        channel_id = str(channel.id)
        if channel_id in self.config["locked_channels"]:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            if overwrite.send_messages is None or overwrite.send_messages is False:
                # Reset send messages permission for @everyone
                overwrite.send_messages = None
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                await ctx.send(f"Channel {channel.mention} unlocked successfully.")
                self.config["locked_channels"].remove(channel_id)
                save_config(self.config)
            else:
                await ctx.send(f"Channel {channel.mention} is already unlocked.")
        else:
            await ctx.send(f"Channel {channel.mention} is not locked.")

    @unlock_channel.error
    async def unlock_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to manage channels.")


async def setup(bot):
    await bot.add_cog(UnlockChannel(bot))

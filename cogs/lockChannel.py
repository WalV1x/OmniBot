import json

import discord
from discord.ext import commands


# Load configuration from config.json
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


# Save configuration to config.json
def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


# ------------------------ COGS ------------------------ #

class LockChannel(commands.Cog, name="LockChannel"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.config = load_config()

    # ------------------------ COGS ------------------------ #

    @commands.command(name="lock", aliases=["lockchannel"], brief="Verrouille le canal")
    @commands.has_permissions(manage_channels=True)
    async def lock_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Verrouille le canal spécifié. Si aucun canal n'est mentionné, le canal actuel sera verrouillé.
        """
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is None or overwrite.send_messages is True:
            overwrite.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(f"Le canal {channel.mention} a été verrouillé avec succès.")
            self.config["locked_channels"].append(channel.id)
            save_config(self.config)
        else:
            await ctx.send(f"Le canal {channel.mention} est déjà verrouillé.")

    @lock_channel.error
    async def lock_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Vous n'avez pas la permission de gérer les canaux.")


async def setup(bot):
    await bot.add_cog(LockChannel(bot))

import json

import discord
from discord.ext import commands


def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
        config["locked_channels"] = [str(channel_id) for channel_id in config.get("locked_channels", [])]
        return config


def save_config(config):
    with open('config.json', 'w') as f:
        # Sauvegarder la configuration en convertissant les identifiants de canal en entiers
        config["locked_channels"] = [int(channel_id) for channel_id in config.get("locked_channels", [])]
        json.dump(config, f, indent=4)


# ------------------------ COGS ------------------------ #

class UnlockChannel(commands.Cog, name="UnlockChannel"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.config = load_config()

    # ------------------------ COGS ------------------------ #

    @commands.command(name="unlock", aliases=["unlockchannel"], brief="Déverrouille le canal")
    @commands.has_permissions(manage_channels=True)
    async def unlock_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Déverrouille le canal spécifié. Si aucun canal n'est mentionné, le canal actuel sera déverrouillé.
        """
        channel = channel or ctx.channel
        channel_id = str(channel.id)
        if channel_id in self.config["locked_channels"]:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            if overwrite.send_messages is None or overwrite.send_messages is False:
                # Réinitialisation de l'autorisation d'envoi de messages pour @everyone
                overwrite.send_messages = None
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                await ctx.send(f"Le canal {channel.mention} a été déverrouillé avec succès.")
                self.config["locked_channels"].remove(channel_id)
                save_config(self.config)
            else:
                await ctx.send(f"Le canal {channel.mention} est déjà déverrouillé.")
        else:
            await ctx.send(f"Le canal {channel.mention} n'est pas verrouillé.")

    @unlock_channel.error
    async def unlock_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Vous n'avez pas la permission de gérer les canaux.")


async def setup(bot):
    await bot.add_cog(UnlockChannel(bot))

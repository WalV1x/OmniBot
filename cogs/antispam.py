import json

import discord
from discord.ext import commands


def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        return config


def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


# ------------------------ COGS ------------------------ #

class AntiSpam(commands.Cog, name="AntiSpam"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.antispam = commands.CooldownMapping.from_cooldown(5, 15, commands.BucketType.member)
        self.too_many_violations = commands.CooldownMapping.from_cooldown(4, 60, commands.BucketType.member)
        self.antispam_enabled = True
        self.config = load_config()

    # ------------------------ COGS ------------------------ #

    # Source: https://www.youtube.com/watch?v=799hRjPiEeQ
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if type(message.channel) is not discord.TextChannel or message.author.bot:
            return

        if not self.antispam_enabled:
            return  # Anti-spam feature is disabled

        bucket = self.antispam.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, don't spam", delete_after=5)
            violations = self.too_many_violations.get_bucket(message)
            check = violations.update_rate_limit()
            if check:
                muted_role_id = self.config.get("muted_role")
                muted_role = message.guild.get_role(muted_role_id)
                if muted_role:
                    await message.author.add_roles(muted_role, reason="Spamming")
                    try:
                        await message.author.send("You have been muted for spamming!")
                    except:
                        pass

    @commands.command(name="antispam", description="Toggle anti-spam feature")
    @commands.has_permissions(administrator=True)
    async def antispam_command(self, ctx):
        if self.antispam_enabled:
            self.antispam_enabled = False
            await ctx.send("Anti-spam feature is now disabled.")
        else:
            self.antispam_enabled = True
            await ctx.send("Anti-spam feature is now enabled.")


async def setup(bot):
    await bot.add_cog(AntiSpam(bot))

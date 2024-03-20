import discord
from discord.ext import commands


# ------------------------ COGS ------------------------ #

class UserInfos(commands.Cog, name="UserInfos"):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------ COGS ------------------------ #

    @commands.command(name="userinfo", aliases=["ui"],
                      brief="Affiche les informations d'un utilisateur")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        embed = discord.Embed(title="User Info", color=member.color)
        embed.set_thumbnail(url=member.avatar.url)  # Utilisation de member.avatar.url
        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="Discriminator", value=member.discriminator, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Status", value=member.status, inline=True)
        embed.add_field(name="Created At", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles[1:]]), inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}",
                         icon_url=ctx.author.avatar.url)  # Utilisation de ctx.author.avatar.url

        await ctx.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(UserInfos(bot))

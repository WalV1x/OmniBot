import discord
from discord.ext import commands
from typing import Optional


# ------------------------ COGS ------------------------ #

class UserInfos(commands.Cog, name="UserInfos"):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------ COGS ------------------------ #

    @commands.command(name="userinfo", aliases=["ui"], brief="Display user information")
    async def userinfo(self, ctx: commands.Context, member: Optional[discord.Member] = None) -> None:
        """Display information about the specified user or the message author if no user is specified."""
        member = member or ctx.author
        roles_str = ", ".join([role.name for role in member.roles[1:]])

        embed = discord.Embed(title="User Information", color=member.color)
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="Discriminator", value=member.discriminator, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Status", value=str(member.status).capitalize(), inline=True)
        embed.add_field(name="Created At", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Roles", value=roles_str if roles_str else "None", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(UserInfos(bot))

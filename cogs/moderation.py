from discord.ext import commands


class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="kick", aliases=["k"], brief="Kick a member")
    @commands.has_permissions(kick_members=True)
    async def kick_member(self, ctx, member: commands.MemberConverter, *, reason="No reason provided"):
        """
        Kick a member from the server.
        Usage: !kick <member_mention> [reason]
        Aliases: k
        """
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked for {reason}.")

    @commands.command(name="ban", aliases=["b"], brief="Ban a member")
    @commands.has_permissions(ban_members=True)
    async def ban_member(self, ctx, member: commands.MemberConverter, *, reason="No reason provided"):
        """
        Ban a member from the server.
        Usage: !ban <member_mention> [reason]
        Aliases: b
        """
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned for {reason}.")

    @commands.command(name="unban", aliases=["ub"], brief="Unban a member")
    @commands.has_permissions(ban_members=True)
    async def unban_member(self, ctx, *, member):
        """
        Unban a member from the server.
        Usage: !unban <member_username#discriminator>
        Aliases: ub
        """
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"{user.mention} has been unbanned.")
                return

        await ctx.send("Member not found in the ban list.")

    @commands.command(name="clear", aliases=["cls"], brief="Clear messages")
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int):
        """
        Clear a specified number of messages from the channel.
        Usage: !clear <amount>
        Aliases: c
        """
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"{amount} messages cleared.", delete_after=5)


async def setup(bot) -> None:
    await bot.add_cog(Moderation(bot))

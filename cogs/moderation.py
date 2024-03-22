import json

import discord
from discord.ext import commands


def load_config():
    with open('config.json', 'r') as file:
        return json.loads(file)


def write_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)


# ------------------------ COGS ------------------------ #

class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # ------------------------ COGS ------------------------ #

    @commands.command(name="mute", aliases=["m"], brief="Mutes a member")
    @commands.has_permissions(mute_members=True)
    async def mute(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """
        Mute a member.
        Usage: !mute <member_mention> [reason]
        Aliases: m
        """
        muted_role_id = self.bot.config.get('muted_role')
        if not muted_role_id:
            await ctx.send("Muted role is not set. Use `!muterole <role>` to set it.")
            return

        muted_role = ctx.guild.get_role(muted_role_id)
        if not muted_role:
            await ctx.send("Muted role not found. Please make sure the role still exists.")
            return

        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f"{member.mention} has been muted for {reason}.")

    @commands.command(name="muterole", brief="Sets the muted role")
    async def set_muted_role(self, ctx, role: discord.Role):
        """
        set a mute role on the server
        Usage: !muterole <mute_role>
        Aliases: /
        """
        self.bot.config['muted_role'] = role.id
        write_config(self.bot.config)
        await ctx.send(f"Muted role set to {role.name}.")

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

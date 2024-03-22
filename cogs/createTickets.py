import asyncio

import discord
from discord.ext import commands


class TicketSystem(commands.Cog, name="TicketSystem"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.group(name="ticket",
                    brief="Command for the ticketing system")
    @commands.has_permissions(administrator=True)
    async def ticket(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a subcommand. Example: !ticket setup")

    @ticket.command(name="setup",
                    brief="Command to create the embed for the ticket")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        embed = discord.Embed(
            title="Support Tickets",
            description="Select a category for your ticket below. A staff member will be with you shortly.",
            color=0x3DD5FA
        )
        embed.set_footer(text="Omnibot - Ticketing Services",
                         icon_url="https://raw.githubusercontent.com/WalV1x/OmniBot/main/img/logo.jpeg")

        # Source : https://guide.pycord.dev/interactions/ui-components/dropdowns
        # Source : https://guide.pycord.dev/interactions/ui-components/buttons

        supportButton = discord.ui.Button(label="Support Ticket", style=discord.ButtonStyle.primary, emoji="📩",
                                          custom_id="support_ticket_button")
        documentationButton = discord.ui.Button(label="Documentation", style=discord.ButtonStyle.link, emoji="📄",
                                                url="https://github.com/WalV1x/OmniBot/blob/main/README.md")

        view = discord.ui.View()
        view.add_item(supportButton)
        view.add_item(documentationButton)

        await ctx.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if interaction.custom_id == "support_ticket_button":
            # Create and send the modal dialog
            modal_embed = discord.Embed(
                title="Issue Details",
                description="Please provide a title and description of your issue.",
                color=0x3DD5FA
            )
            modal = await interaction.channel.send(embed=modal_embed)
            await modal.add_reaction('✅')  # Optional: Add a reaction for users to close the modal
            # Now, you can wait for user input here, like waiting for a message or reaction
            # You can handle the user's input accordingly
            # For example:
            try:
                response = await self.bot.wait_for("message", timeout=300.0,
                                                   check=lambda m: m.author == interaction.user)
                await interaction.channel.send(f"Thank you for your response: {response.content}")
            except asyncio.TimeoutError:
                await interaction.channel.send("You took too long to respond.")


async def setup(bot):
    await bot.add_cog(TicketSystem(bot))

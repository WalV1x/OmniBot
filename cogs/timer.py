import discord
from discord.ext import commands
import json
import asyncio
import datetime

class AutomatedMessages(commands.Cog, name="Automated Messages"):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def write_config(self, config):
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

    @commands.group(name="timers", invoke_without_command=True)
    async def timers(self, ctx):
        """Manage automated message timers."""
        command_list = "\n".join([f"{command.name}: {command.help}" for command in self.timers.commands])
        await ctx.send(f"Available subcommands:\n{command_list}")

    @timers.command(name="add", aliases=["a"])
    async def add_timer(self, ctx, interval_minutes: int, *, message: str):
        config = await self.load_config()
        timers = config.get("timers", [])
        timer_id = len(timers) + 1  # Generate a new ID for the timer
        new_timer = {
            "id": timer_id,
            "interval_minutes": interval_minutes,
            "message": message,
            "last_sent": datetime.datetime.utcnow().isoformat()
        }
        timers.append(new_timer)
        config["timers"] = timers
        await self.write_config(config)
        await ctx.send(f"Timer added! Message will be sent every {interval_minutes} minutes.")

    @timers.command(name="remove", aliases=["r"])
    async def remove_timer(self, ctx, timer_id: int):
        config = await self.load_config()
        timers = config.get("timers", [])
        for timer in timers:
            if timer["id"] == timer_id:
                timers.remove(timer)
                config["timers"] = timers
                await self.write_config(config)
                await ctx.send(f"Timer with ID {timer_id} removed.")
                return
        await ctx.send("Timer not found.")


    @timers.command(name="list", aliases=["l"])
    async def list_timers(self, ctx):
        config = await self.load_config()
        timers = config.get("timers", [])
        if not timers:
            await ctx.send("No active timers.")
            return
        timer_list = "\n".join([f"ID: {timer['id']}, Interval: {timer['interval_minutes']} minutes, Message: {timer['message']}" for timer in timers])
        await ctx.send(f"Active Timers:\n{timer_list}")


    @timers.command(name="set", aliases=["s"])
    async def set_timer(self, ctx, timer_id: int, interval_minutes: int, *, message: str):
        config = await self.load_config()
        timers = config.get("timers", [])
        for timer in timers:
            if timer["id"] == timer_id:
                timer["interval_minutes"] = interval_minutes
                timer["message"] = message
                await self.write_config(config)
                await ctx.send(f"Timer with ID {timer_id} updated.")
                return
        await ctx.send("Timer not found.")

    async def send_timer_messages(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            # Logic to send timer messages
            await asyncio.sleep(60)  # Check every minute

async def setup(bot) -> None:
    await bot.add_cog(AutomatedMessages(bot))
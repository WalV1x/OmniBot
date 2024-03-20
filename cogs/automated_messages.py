import asyncio
import datetime
import json
import os

from discord.ext import commands


class AutomatedMessages(commands.Cog, name="Automated Messages"):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def load_config(self, config_path: str = "config.json") -> dict:
        """
        Load bot configuration from a JSON file.

        Args:
            config_path (str): Path to the configuration file.

        Returns:
            dict: Configuration data.
        """
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
        with open(config_path) as file:
            return json.load(file)

    async def write_config(self, config, config_path: str = "config.json") -> None:
        """
        Write bot configuration to a JSON file.

        Args:
            config (dict): Configuration data.
            config_path (str): Path to the configuration file.
        """
        with open(config_path, "w") as file:
            json.dump(config, file, indent=4)

    @commands.group(name="timers", invoke_without_command=True)
    async def timers(self, ctx):
        """
        Manage automated message timers.

        Subcommands:
        - add (a): Add a new timer.
        - remove (r): Remove an existing timer.
        - list (l): List all active timers.
        - set (s): Update an existing timer.
        """
        command_list = "\n".join([f"{command.name}: {command.help}" for command in self.timers.commands])
        await ctx.send(f"Available subcommands:\n{command_list}")

    @timers.command(name="add", aliases=["a"])
    async def add_timer(self, ctx, interval_minutes: int, *, message: str):
        """
        Add a new timer.

        Args:
        - interval_minutes (int): Interval in minutes between messages.
        - message (str): Message to send.

        Example:
        !timers add 30 Hello, world!
        """
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
        """
        Remove an existing timer.

        Args:
        - timer_id (int): ID of the timer to remove.

        Example:
        !timers remove 1
        """
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
        """
        List all active timers.
        """
        config = await self.load_config()
        timers = config.get("timers", [])
        if not timers:
            await ctx.send("No active timers.")
            return
        timer_list = "\n".join(
            [f"ID: {timer['id']}, Interval: {timer['interval_minutes']} minutes, Message: {timer['message']}" for timer
             in timers])
        await ctx.send(f"Active Timers:\n{timer_list}")

    @timers.command(name="set", aliases=["s"])
    async def set_timer(self, ctx, timer_id: int, interval_minutes: int, *, message: str):
        """
        Update an existing timer.

        Args:
        - timer_id (int): ID of the timer to update.
        - interval_minutes (int): New interval in minutes between messages.
        - message (str): New message to send.

        Example:
        !timers set 1 60 Updated message
        """
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
            config = await self.load_config()
            timers = config.get("timers", [])
            for timer in timers:
                last_sent = datetime.datetime.fromisoformat(timer["last_sent"])
                interval = datetime.timedelta(minutes=timer["interval_minutes"])
                if datetime.datetime.utcnow() - last_sent >= interval:
                    channel_id = timer.get("channel_id")
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.send(timer["message"])
                        timer["last_sent"] = datetime.datetime.utcnow().isoformat()
                        await self.write_config(config)
            await asyncio.sleep(60)  # Check every minute


async def setup(bot) -> None:
    await bot.add_cog(AutomatedMessages(bot))

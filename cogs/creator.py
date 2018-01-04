import asyncio
import datetime

import time
import io
import textwrap
import subprocess
import traceback
import inspect

from discord.ext import commands
from assets import utils
from contextlib import redirect_stdout

class Creator:
    """ Commands for the creator """

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    @commands.command()
    @commands.check(utils.is_owner)
    async def reload(self, ctx, name: str = None):
        """ Reloads an extension. """
        if name is None or name == "*":
            try:
                for extension in self.bot.extensions:
                    self.bot.unload_extension(extension)
                    self.bot.load_extension(extension)
            except Exception as e:
                await ctx.send(f"```\n{e}```")
                return
            
            await ctx.send(f"**{ctx.author.name}**, reloaded all extensions")
        else: 
            try:
                self.bot.unload_extension(f"cogs.{name}")
                self.bot.load_extension(f"cogs.{name}")
            except Exception as e:
                await ctx.send(f"```\n{e}```")
                return
            await ctx.send(f"**{ctx.author.name}**, reloaded extension **{name}.py**")

    @commands.command()
    @commands.check(utils.is_owner)
    async def load(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```diff\n- {e}```")
            return
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command()
    @commands.check(utils.is_owner)
    async def unload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```diff\n- {e}```")
            return
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.command(aliases=["reboot", "panic"])
    @commands.check(utils.is_owner)
    async def stop(self, ctx):
        """ Reboot the bot """
        time.sleep(1)
        await self.bot.logout()

    @commands.command(aliases=["exec", "shell"])
    @commands.check(utils.is_owner)
    async def execute(self, ctx, *, text: str):
        """ Do a shell command. """
        text_parsed = list(filter(None, text.split(" ")))
        output = subprocess.check_output(text_parsed).decode()
        await ctx.send(f"```shell\n{output}\n```")

def setup(bot):
    bot.add_cog(Creator(bot))

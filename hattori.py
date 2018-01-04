import json
import os

from discord.ext.commands import HelpFormatter
from data import Bot

import ruamel.yaml as yaml
import discord

description = """
Hattori, a discord bot for gathering brawlhalla statistics.
"""

class HelpFormat(HelpFormatter):
    async def format_help_for(self, context, command_or_bot):
        if (isinstance(context.channel, discord.DMChannel) or context.channel.permissions_for(context.guild.me).add_reactions):
            await context.message.add_reaction(chr(0x2709))
        return await super().format_help_for(context, command_or_bot)

print("Attempting to login")

help_attrs = dict(hidden=True)
bot = Bot(command_prefix=[f"<@!396042509408665603> ", f"<@396042509408665603> "], pm_help=True, help_attrs=help_attrs, formatter=HelpFormat())

with open("config.yml") as c:
    data = yaml.safe_load(c)
    token = data['configuration']['token']

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

bot.run(token)

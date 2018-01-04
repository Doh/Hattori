import discord
import datetime, re
import rethinkdb as r
from discord.ext.commands import AutoShardedBot, errors
import ruamel.yaml as yaml

with open("config.yml") as c:
    data = yaml.safe_load(c)

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        _help = await ctx.bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
    else:
        _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

    for page in _help:
        await ctx.send(page)

class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_message(self, ctx):

        if not self.is_ready() or ctx.author.bot or not (isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).send_messages) or ctx.author.id in data["blacklists"]:
            return

        await self.process_commands(ctx)

    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            await send_cmd_help(ctx)

        elif isinstance(err, errors.CommandInvokeError):
            await ctx.send(f"**{ctx.author.name}**, an error occured while executing the command\n```diff\n- {err.original}\n```")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"**{ctx.author.name}**, this command is currently on cooldown, please wait {err.retry_after:.0f} seconds.")

        elif isinstance(err, errors.CommandNotFound):
            pass

    async def on_ready(self):
        print(f'Connected to Discord API')
        r.connect(data['database']['host'], data['database']['port']).repl()
        await self.change_presence(status=discord.Status.online, game=discord.Game(name=data['configuration']['status'])) 

import time
import discord

from discord.ext import commands
from assets import http
from io import BytesIO
import ruamel.yaml as yaml

with open("./config.json") as c:
    config = yaml.safe_load(c) 
    website = config["configuration"]["website"]
    invite = config["configuration"]["invite"]
    support = config["configuration"]["support"]

class Default:
    """ Default Commands that every bot has """

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(aliases=["pong"])
    async def ping(self, ctx):
        """ Pong! Tests if the bot is working """
        before = time.monotonic()
        message = await ctx.send("Pong!")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Ping `{int(ping)}ms`")

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        """ Gets a members avatar """
        if member is None:
            member = ctx.author

        byte = BytesIO(await http.get(member.avatar_url_as(format="png")))
        await ctx.send(file=discord.File(byte, filename=f"{member.id}.png"))  

    @commands.command()
    async def about(self, ctx):
        """ About Hattori """
        embed = discord.Embed(description="Discord bot for gathering Brawlhalla statistics", colour=0x420605)
        embed.set_author(name=ctx.bot.user.name, icon_url="https://i.imgur.com/DUs50QA.png")
        embed.add_field(name="Developer", value="Doh", inline=True)
        embed.add_field(name="Library", value=f"discord.py {discord.__version__}", inline=True)
        embed.add_field(name="Guilds", value=len(ctx.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(ctx.bot.users), inline=True)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)

        return await ctx.send(embed=embed)

    @commands.command()
    async def website(self, ctx):
        """ Get the website """
        await ctx.send(f"<:me:396049877546565664> | **{ctx.author.name}**, <{website}>")

    @commands.command()
    async def invite(self, ctx):
        """ Invite me to your server """
        await ctx.send(f"<:me:396049877546565664> | **{ctx.author.name}**, <{invite}>")

    @commands.command(aliases=["feedback"])
    async def support(self, ctx):
        """ Get an invite to our support server! """
        return await ctx.send(f"<:me:396049877546565664> | **{ctx.author.name}**, <{support}>")

def setup(bot):
    bot.add_cog(Default(bot))

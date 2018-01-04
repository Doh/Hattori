import discord
from discord.ext import commands
from assets import utils, http
import asyncio
import rethinkdb as r 
import ruamel.yaml as yaml
import json

list_message = """```rb
[1] Steam username, example
[2] Steam ID (64), 76561198404906386
```
"""

with open("./config.yml") as c:
    config = yaml.safe_load(c)
    token = config["configuration"]["api_keys"]["brawlhalla"]
    lepeli = config["configuration"]["api_keys"]["lepeli"]
    twitch = config["configuration"]["api_keys"]["twitch"]

class Other:
    """ Other commands """

    def __init__(self, bot):
        self.bot = bot
        
    async def resolve_brawlhalla(self, steamid):
        if utils.is_number(steamid): # User specified Steam ID
            req, data = await http.get(f"https://api.brawlhalla.com/search?steamid={steamid}&api_key={token}", as_json=True)
            if not data:
                return None
            else:
                return data
        else: # User specified Steam Username
            lepeli_req, lepeli_data = await http.get(f"https://api.lepeli.fr/steamid/?s={steamid}&key={lepeli}", as_json=True)
            if lepeli_data['status'] == 404:
                return None
            else:
                steamid64 = lepeli_data['id']['steamid64']
                req, data = await http.get(f"https://api.brawlhalla.com/search?steamid={steamid64}&api_key={token}", as_json=True)
                
                if not data:
                    return None
                else:
                    return data

    @commands.command(aliases=["live"])
    async def streaming(self, ctx):
        """ Checks if Brawlhalla is streaming on Twitch """
        req, data = await http.get(f"https://api.twitch.tv/kraken/streams/brawlhalla?client_id={twitch}", as_json=True)
        if data["stream"] is None or data is None:
            await ctx.send(f"<:twitch:366951056078536706> | **{ctx.author.name}**, brawlhalla seems to not be streaming right now")
        else:
            embed = discord.Embed(title="Brawlhalla", description=data["stream"]["game"], colour=0x6441A4)
            embed.add_field(name="Watching", value=utils.number(data["stream"]["viewers"]), inline=True)
            embed.add_field(name="Followers", value=utils.number(data["stream"]["channel"]["followers"]), inline=True)
            embed.set_thumbnail(url=data["stream"]["channel"]["logo"])

            await ctx.send(embed=embed)

    @commands.command()
    async def alerts(self, ctx):
        """ Enables streaming alerts for Brawlhallas Twitch """
        await ctx.send(f"🔐 | **{ctx.author.name}**, this feature is currently **coming soon**")

    @commands.command(aliases=["remember"])
    async def claim(self, ctx, user: str = None):
        """ Remembers your brawlhalla user so you don't need to keep entering your ID """
        data = list(r.db("hattori").table("claimed").filter(r.row['user'] == str(ctx.author.id)).run())

        async with ctx.channel.typing():
            if user is None:
                if len(data) == 0:
                    return await ctx.send(f"**{ctx.author.name}**, you are currently **not registered** to be claimed")
                else:
                    return await ctx.send(f"**{ctx.author.name}**, you are currently **registered** under **{data[0]['brawlhalla']}**")
            else:
                resolved = await self.resolve_brawlhalla(steamid=user)

                if resolved is None:
                    return await ctx.send(f"**{ctx.author.name}**, that user couldn't be resolved, here are some examples of what you should be inserting.\n{list_message}")
                else:
                    if len(data) == 0:
                        r.db("hattori").table("claimed").insert({ "user" : str(ctx.author.id), "brawlhalla" : str(resolved['brawlhalla_id']) }).run()
                        return await ctx.send(f"**{ctx.author.name}**, you have successfully **registered** under **{user}**") 
                    else:
                        if data[0]['brawlhalla'] == str(resolved['brawlhalla_id']):
                            return await ctx.send(f"**{ctx.author.name}**, you are already registered under **{user}**")

                        message = await ctx.send(f"**{ctx.author.name}**, you are currently registered under **{data[0]['brawlhalla']}**, are you sure you want to update it to **{user}**? Respond with either **yes** or **no**.", delete_after=30.0)
                        def check(message):
                            return message.author.id == ctx.author.id and message.channel.id == ctx.channel.id and message.content.lower() == "yes" or message.content.lower() == "no"

                        try:
                            result = await ctx.bot.wait_for("message", check=check, timeout=30.0)
                            if result.content.lower() == "yes":
                                r.db("hattori").table("claimed").filter(r.row['user'] == str(ctx.author.id)).update({'brawlhalla' : str(resolved['brawlhalla_id'])}).run()
                                return await ctx.send(f"**{ctx.author.name}**, you have successfully **registered** under **{user}**")
                            elif result.content.lower() == "no":
                                return await ctx.send(f"**{ctx.author.name}**, the confirmation has been cancelled due to a answer of **no**.")
                        except asyncio.TimeoutError as e:
                            return await ctx.send(f"**{ctx.author.name}**, the confirmation has been timed out after 30 seconds.")

    @commands.command(aliases=["unremember"])
    async def unclaim(self, ctx):
        """ Unclaims your brawlhalla user #, you will no longer be remembered """
        data = list(r.db("hattori").table("claimed").filter(r.row['user'] == str(ctx.author.id)).run())

        async with ctx.channel.typing():
                if len(data) == 0:
                    return await ctx.send(f"**{ctx.author.name}**, you are currently **not registered**")
                else:
                    r.db("hattori").table("claimed").filter(r.row['user'] == str(ctx.author.id)).delete().run()
                    return await ctx.send(f"**{ctx.author.name}**, successfully unregistered from **{data[0]['brawlhalla']}**")

def setup(bot):
    bot.add_cog(Other(bot))

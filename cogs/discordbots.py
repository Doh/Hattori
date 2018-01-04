import discord
from assets import http
import aiohttp
import json
import ruamel.yaml as yaml

with open("./config.yml") as c:
    config = yaml.safe_load(c)
    discordbots = config["configuration"]["api_keys"]["discordbots"]

class DiscordBots:
    """ Handles post requests to discordbot sites """

    def __init__(self, bot):
        self.bot = bot

    async def post_guild_statistics(self, server_count=None):
        try:
            for bot_list in discordbots:
            	await http.post(bot_list, as_json=True, headers={"Authorization" : discordbots[bot_list]}, data={"server_count" : server_count})
        except Exception as e:
            print(e)

    async def channel_update(self, guild=None, status=None):
        embed = discord.Embed(description=status, colour=0x420605)
        embed.set_author(name="Hattori", icon_url="https://i.imgur.com/DUs50QA.png")
        embed.add_field(name="Name", value=guild.name, inline=True)
        embed.add_field(name="Guild #", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner, inline=True)
        embed.add_field(name="Owner #", value=guild.owner.id, inline=True)
        embed.set_footer(text=f"Hattori is now in {len(self.bot.guilds)} guilds.")
        embed.set_thumbnail(url=guild.icon_url_as(format="png"))

        await self.bot.get_channel(356248863398559754).send(embed=embed)

    async def on_guild_join(self, guild):
        await self.post_guild_statistics(server_count=len(self.bot.guilds))
        await self.channel_update(guild=guild, status="Added to a Guild with {} members".format(guild.member_count))
    
    async def on_guild_remove(self, guild):
        await self.post_guild_statistics(server_count=len(self.bot.guilds))
        await self.channel_update(guild=guild, status="Removed from a Guild with {} members".format(guild.member_count))
 
def setup(bot):
    bot.add_cog(DiscordBots(bot))

import datetime, re
import discord

from bs4 import BeautifulSoup
from discord.ext import commands
from assets import http, utils, parser
from io import BytesIO
import ruamel.yaml as yaml
import rethinkdb as r

with open("./config.yml") as c:
    config = yaml.safe_load(c)
    token = config["configuration"]["api_keys"]["brawlhalla"]
    lepeli = config["configuration"]["api_keys"]["lepeli"]
    footer = config["configuration"]["footer"]
    color = config["configuration"]["color"]

    legends_json = config["legends"]
    conversions = config["conversions"]
    emoji = config["emojis"]

class Brawlhalla:
    """ The brawlhalla based commands """

    def __init__(self, bot):
        self.bot = bot

    async def claimed_user(self, user_id):
        data = list(r.db("hattori").table("claimed").filter(r.row['user'] == str(user_id)).run())
        if len(data) == 0:
            return False
        else:
            return data[0]['brawlhalla']

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        else:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

        for page in _help:
            await ctx.send(page)

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


    @commands.command()
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    async def resolve(self, ctx, steamID: str):
        """ Resolves a users brawlhalla # from a steam username or # """
        async with ctx.channel.typing():
            resolved = await self.resolve_brawlhalla(steamid=steamID)
            if resolved is None:
                return await ctx.send(f"**{ctx.author.name}**, i could not find any brawlhalla user based on your search. This is due to either you specifying a invalid search or what you queried is already a brawlhalla user id")
            else:
                return await ctx.send(f"<:me:396049877546565664> | **{ctx.author.name}**, successfully resolved the brawlhalla user.\n```rb\n{resolved['name']} # {resolved['brawlhalla_id']}\n```")             

    @commands.command()
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    async def user(self, ctx, user: str = None, *, flag: str = None):
        """ Gets a brawlhalla users statistics. You can specify flags for 
        specific statistics with "--flag [flag]", these flags include
  
        ranked:
            The ranked statistics of the user
        legends:
            The amount and list of legends the user has
        clan:
            The clan that the users in, if none it'll send a error
        other:
            Get other statistics, such as most played legend etc.
        
        Example:
            @Hattori user 227191 --flag legends

        Specifying no flag will lead to the general stats being shown
        """  
        async with ctx.channel.typing():
            claimed_or_not = await self.claimed_user(ctx.author.id)
            if claimed_or_not != False:
                req, data = await http.get(f"https://api.brawlhalla.com/player/{claimed_or_not}/stats?api_key={token}", as_json=True)
                if data is None:
                    return await ctx.send(f"**{ctx.author.name}**, i could not find any brawlhalla user based on your search, You can either specify a steam username, steam id or a brawlhalla id. If you are not sure what the users brawlhalla id is you can use the resolve command.")

                embed = discord.Embed(title=data['name'].title(), description="Level {}".format(utils.number(data['level'])), colour=color)
                embed.add_field(name="Games Played", value=utils.number(data['games']), inline=True)
                embed.add_field(name="Games Won", value=utils.number(data['wins']), inline=True)
                embed.add_field(name="Experience", value=utils.number(data['xp']), inline=True)
                
                embed.add_field(name="Bomb Damage", value=utils.number(data['damagebomb']), inline=True)
                embed.add_field(name="Mine Damage", value=utils.number(data['damagemine']), inline=True)
                embed.add_field(name="Spikeball Damage", value=utils.number(data['damagespikeball']), inline=True)
                embed.add_field(name="Sidekick Damage", value=utils.number(data['damagesidekick']), inline=True)

                embed.add_field(name="Bomb KO", value=utils.number(data['kobomb']), inline=True)
                embed.add_field(name="Mine KO", value=utils.number(data['komine']), inline=True)
                embed.add_field(name="Spikeball KO", value=utils.number(data['kospikeball']), inline=True)
                embed.add_field(name="Sidekick KO", value=utils.number(data['kosidekick']), inline=True)
                embed.add_field(name="Snowball Hit", value=utils.number(data['hitsnowball']), inline=True)

                embed.set_footer(text=footer['text'], icon_url=footer['icon'])

                return await ctx.send(embed=embed)
            else:
                return await self.send_cmd_help(ctx)

            resolved = await self.resolve_brawlhalla(steamid=user)

            if resolved is None:
                pass
            else:
                user = int(resolved['brawlhalla_id'])         

            if flag is None:
                req, data = await http.get(f"https://api.brawlhalla.com/player/{user}/stats?api_key={token}", as_json=True)
                if data is None:
                    return await ctx.send(f"**{ctx.author.name}**, i could not find any brawlhalla user based on your search, You can either specify a steam username, steam id or a brawlhalla id. If you are not sure what the users brawlhalla id is you can use the resolve command.")

                embed = discord.Embed(title=data['name'].title(), description="Level {}".format(utils.number(data['level'])), colour=color)
                embed.add_field(name="Games Played", value=utils.number(data['games']), inline=True)
                embed.add_field(name="Games Won", value=utils.number(data['wins']), inline=True)
                embed.add_field(name="Experience", value=utils.number(data['xp']), inline=True)
                
                embed.add_field(name="Bomb Damage", value=utils.number(data['damagebomb']), inline=True)
                embed.add_field(name="Mine Damage", value=utils.number(data['damagemine']), inline=True)
                embed.add_field(name="Spikeball Damage", value=utils.number(data['damagespikeball']), inline=True)
                embed.add_field(name="Sidekick Damage", value=utils.number(data['damagesidekick']), inline=True)

                embed.add_field(name="Bomb KO", value=utils.number(data['kobomb']), inline=True)
                embed.add_field(name="Mine KO", value=utils.number(data['komine']), inline=True)
                embed.add_field(name="Spikeball KO", value=utils.number(data['kospikeball']), inline=True)
                embed.add_field(name="Sidekick KO", value=utils.number(data['kosidekick']), inline=True)
                embed.add_field(name="Snowball Hit", value=utils.number(data['hitsnowball']), inline=True)

                embed.set_footer(text=footer['text'], icon_url=footer['icon'])

                return await ctx.send(embed=embed)
            else:
                flags = parser.parse_arguments(ctx, args=flag)
                if flags == "legends":
                    req, data = await http.get(f"https://api.brawlhalla.com/player/{user}/stats?api_key={token}", as_json=True)
                    if data is None:
                        return await ctx.send(f"**{ctx.author.name}**, i could not find any brawlhalla user based on your search, if you would like to get a users brawlhalla ID from there steam username or id, please use the resolve command.")

                    legends_sorted = sorted(data['legends'], key=lambda l: l['level'], reverse=True)
                    legends = []

                    for legend in legends_sorted:
                        legends.append(legend['legend_name_key'].title())

                    return await ctx.send("<:me:396049877546565664> | **{}**, list of **{}** legends for **{}** ({})\n```fix\n{}\n```".format(ctx.author.name, len(legends), data['name'].title(), data['brawlhalla_id'], ", ".join(legends)))
                elif flags == "clan":
                    req, data = await http.get(f"https://api.brawlhalla.com/player/{user}/stats?api_key={token}", as_json=True)
                    if data is None:
                        return await ctx.send(f"**{ctx.author.name}**, i could not find any brawlhalla user based on your search, if you would like to get a users brawlhalla ID from there steam username or id, please use the resolve command.")

                    try:
                        embed = discord.Embed(title=f"{data['clan']['clan_name']}", description=f"# {data['clan']['clan_id']}", colour=color)
                        embed.add_field(name="Clan Experience", value=utils.number(data['clan']['clan_xp']), inline=True)
                        embed.add_field(name="Personal Experience", value=utils.number(data['clan']['personal_xp']), inline=True)
                        embed.set_footer(text=footer['text'], icon_url=footer['icon'])
                        return await ctx.send(embed=embed)     
                    except Exception as e:
                        return await ctx.send(f"**{ctx.author.name}**, brawlhalla user **{data['name']}** is not in a clan")
                elif flags == "ranked":
                    req, data = await http.get(f"https://api.brawlhalla.com/player/{user}/ranked?api_key={token}", as_json=True)
                    if data is None:
                        return await ctx.send(f"**{ctx.author.name}**, i could not find any brawlhalla user based on your search, if you would like to get a users brawlhalla ID from there steam username or id, please use the resolve command.")

                    embed = discord.Embed(title=f"{data['name'].title()}, {data['region']}", description=data['tier'], colour=color)
                    embed.add_field(name="Wins", value=data['wins'], inline=True)
                    embed.add_field(name="Games", value=data['games'], inline=True)
                    embed.add_field(name="Rating", value=data['rating'], inline=True)
                    embed.add_field(name="Peak Rating", value=data['peak_rating'], inline=True)
                    embed.add_field(name="Global Rank", value=data['global_rank'], inline=True)
                    embed.add_field(name="Region Rank", value=data['region_rank'], inline=True)
                    embed.set_footer(text=footer['text'], icon_url=footer['icon'])

                    return await ctx.send(embed=embed)
               	elif flags == "other":
               		req, data = await http.get(f"https://api.brawlhalla.com/player/{user}/stats?api_key={token}", as_json=True)
                	if data is None:
                		return await ctx.send(f"**{ctx.author.name}**, i could not find any brawlhalla user based on your search, if you would like to get a users brawlhalla ID from there steam username or id, please use the resolve command.")

                	async def get_legend_highest(search, data=data):
	                	legends_array = []
	                	count = max(min(5, 25), 5)
	                	sorted_legends = sorted(data['legends'], key=lambda l: l[search], reverse=True)

	                	for legend in sorted_legends:
	                		legends_array.append(legend['legend_name_key'].title())

	                	return legends_array[0]

	               	most_levelled_legend = await get_legend_highest('level')
	               	most_played_legend = await get_legend_highest('matchtime')
	               	most_won_legend = await get_legend_highest('wins')

                	embed = discord.Embed(title=f"{data['name'].title()}", description="Other Statistics", colour=color)
                	embed.add_field(name="Most Played Legend", value=most_played_legend, inline=True)
                	embed.add_field(name="Most Levelled Legend", value=most_levelled_legend, inline=True)
                	embed.add_field(name="Most Won Legend", value=most_won_legend, inline=True)
                	embed.set_footer(text=footer['text'], icon_url=footer['icon'])

                	return await ctx.send(embed=embed)
                else:
                    return await ctx.send(f"**{ctx.author.name}**, you have specified an unknown flag")

    @commands.command()
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    async def clan(self, ctx, clanID: int, *, flag: str = None):
        """ Gets a brawlhalla clans statistics. You can specify flags for 
        specific statistics with "--flag [flag]", these flags include
  
        members:
            The members in the clan
        
        Example:
            @Hattori clan 1 --flag members

        Specifying no flag will lead to the general stats being shown
        """  
        async with ctx.channel.typing():
            if flag is None:
                req, data = await http.get(f"https://api.brawlhalla.com/clan/{clanID}/?api_key={token}", as_json=True)
                if data is None:
                    return await ctx.send(f"**{ctx.author.name}**, i could not find any brawlhalla clan based on your search.")

                embed = discord.Embed(title=f"{data['clan_name']}", description=f"# {data['clan_id']}", colour=color)
                embed.add_field(name="Clan Experience", value=utils.number(data['clan_xp']), inline=True)
                embed.add_field(name="Clan Creation Date", value=utils.date(datetime.datetime.fromtimestamp(data['clan_create_date'])), inline=True)
                embed.set_footer(text=footer['text'], icon_url=footer['icon'])
                return await ctx.send(embed=embed)   
            else:
                flags = parser.parse_arguments(ctx, args=flag)
                if flags == "members":
                    req, data = await http.get(f"https://api.brawlhalla.com/clan/{clanID}/?api_key={token}", as_json=True)
                    if data is None:
                        return await ctx.send(f"**{ctx.author.name}**, i could not find any brawlhalla clan based on your search.")

                    members_sorted = sorted(data['clan'], key=lambda m: m['join_date'], reverse=True)
                    members = []

                    for member in members_sorted:
                        members.append(member['name'].title())

                    return await ctx.send("<:me:396049877546565664> | **{}**, list of **{}** members in **{}** ({})\n```fix\n{}\n```".format(ctx.author.name, len(members), data['clan_name'].title(), data['clan_id'], ", ".join(members)))
                else:
                    return await ctx.send(f"**{ctx.author.name}**, you have specified an unknown flag")

    @commands.command()
    # @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    async def legend(self, ctx, legendID: str, *, flag: str = None):
        """ Gets a brawlhalla legends information. You can specify flags for 
        specific statistics with "--flag [flag]", these flags include
  
        preview:
            The image preview of the legend
        
        Example:
            @Hattori legend 36 --flag preview

        Specifying no flag will lead to the general stats being shown
        """  
        async with ctx.channel.typing():
            try:
                legendID = conversions[legendID.lower()]
            except Exception as e:
                pass

            req, data = await http.get(f"https://api.brawlhalla.com/legend/{legendID}/?api_key={token}", as_json=True)
            if data is None:
                return await ctx.send(f"**{ctx.author.name}**, i could not find any brawlhalla legend based on your search.")

            if flag is None:
	            embed = discord.Embed(title=f"{data['bio_name']}, {data['bio_aka']}", description=data['bio_quote'], colour=color)

	            embed.add_field(name="Bot Name", value=data['bot_name'], inline=True)
	            embed.add_field(name="Weapon 1", value=data['weapon_one'], inline=True)
	            embed.add_field(name="Weapon 2", value=data['weapon_two'], inline=True)
	            
	            embed.add_field(name="Strength", value=data['strength'], inline=True)
	            embed.add_field(name="Dexterity", value=data['dexterity'], inline=True)
	            embed.add_field(name="Defense", value=data['defense'], inline=True)
	            embed.add_field(name="Speed", value=data['speed'], inline=True)

	            embed.set_thumbnail(url=legends_json[data['bio_name'].lower().replace("bödvar", "bodvar")])
	            embed.set_footer(text=data['bio_text'])

	            await ctx.send(embed=embed)
            else:
                flags = parser.parse_arguments(ctx, args=flag)

                if flags == "preview":
                    href = legends_json[data['bio_name'].lower().replace("bödvar", "bodvar")]
                    bio = BytesIO(await http.get(href))

                    await ctx.send(content="{} | **{}**, preview for **{}**".format(discord.utils.get(ctx.bot.get_guild(379112475737718796).emojis, name=data['bio_name'].lower().replace("bödvar", "bodvar").replace(" ", "").replace("hattori", "me")), ctx.author.name, data['bio_name']), file=discord.File(bio, filename=f"{data['bio_name'].lower()}.png"))

    @commands.command()
    async def legends(self, ctx):
        """ Gets all brawlhalla legends """
        await ctx.send(f"🔐 | **{ctx.author.name}**, this feature is currently **coming soon** on brawlhalla's api, please wait as we will add this as soon as it releases!")

    @commands.command(aliases=["wikipedia"])
    async def wiki(self, ctx, *, search: str):
        """ Searches Brawlhalla's wikipedia, coming soon """
        await ctx.send(f"🔐 | **{ctx.author.name}**, this feature is currently in developement :)")

    @commands.command()
    async def social(self, ctx):
        """ Gets Brawlhalla's social links """
        message = """```rb
Steam # http://steamcommunity.com/app/291550
Wiki # http://wiki.brawlhalla.com/
Rankings # http://www.brawlhalla.com/rankings
Reddit # http://brawlhalla.reddit.com
Home # http://www.brawlhalla.com
Twitch # http://www.twitch.tv/brawlhalla
Twitter # http://twitter.com/brawlhalla
Youtube # http://www.youtube.com/user/brawlhalla
Facebook # http://www.facebook.com/Brawlhalla/```
        """

        await ctx.send(f"<:bodvar:396509817079857154> | **{ctx.author.name}**, displaying all brawlhalla social links.\n{message}")
        
def setup(bot):
    bot.add_cog(Brawlhalla(bot))

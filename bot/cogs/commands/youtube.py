import discord
from discord.ext import commands
import urllib.parse
import urllib.request
import re

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='yt', aliases=['youtube'])
    async def search_youtube(self, ctx, *, search_query):
        query_string = urllib.parse.urlencode({'search_query': search_query})
        html_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
        search_results = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())
        if len(search_results) > 0:
            result_message = f"**▶ | Here are your search results:- https://www.youtube.com/watch?v={search_results[0]} **"
            await ctx.send(result_message)
        else:
            await ctx.send('No search results found.')
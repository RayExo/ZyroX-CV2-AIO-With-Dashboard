import discord
from discord.ext import commands
import aiosqlite
import re
import asyncio

class AutoReactListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'db/autoreact.db'
        self.rate_limited_users = set()

    async def get_triggers(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT trigger, emojis FROM autoreact WHERE guild_id = ?", (guild_id,))
            return await cursor.fetchall()

    async def add_rate_limit(self, user_id):
        self.rate_limited_users.add(user_id)
        await asyncio.sleep(5)
        self.rate_limited_users.remove(user_id)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        if message.author.id in self.rate_limited_users:
            return

        triggers = await self.get_triggers(message.guild.id)
        if not triggers:
            return

        content = message.content.strip().lower()
        for trigger, emojis in triggers:
            if content == trigger:
                emoji_list = emojis.split()
                for emoji in emoji_list:
                    try:
                        
                        if re.match(r"<a?:\w+:\d+>", emoji):
                            emoji_obj = discord.PartialEmoji.from_str(emoji)
                        else:
                            
                            emoji_obj = emoji

                        await message.add_reaction(emoji_obj)
                    except discord.errors.NotFound:
                        continue
                    except discord.errors.Forbidden:
                        continue
                    except discord.errors.HTTPException:
                        continue
                    
                await self.add_rate_limit(message.author.id)
                break


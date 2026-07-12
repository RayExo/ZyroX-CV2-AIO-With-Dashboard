import discord
import aiosqlite
import json
import re
import asyncio
from discord.ext import commands

class greet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_queue = {}
        self.processing = set()

    async def safe_format(self, text, placeholders):
        placeholders_lower = {k.lower(): v for k, v in placeholders.items()}
        def replace_var(match):
            var_name = match.group(1).lower()
            return str(placeholders_lower.get(var_name, f"{{{var_name}}}"))
        return re.sub(r"\{(\w+)\}", replace_var, text or "")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id not in self.join_queue:
            self.join_queue[member.guild.id] = []
        self.join_queue[member.guild.id].append(member)
        if member.guild.id not in self.processing:
            self.processing.add(member.guild.id)
            await self.process_queue(member.guild)

    async def process_queue(self, guild):
        while self.join_queue[guild.id]:
            member = self.join_queue[guild.id].pop(0)
            async with aiosqlite.connect("db/welcome.db") as db:
                async with db.execute("SELECT welcome_type, welcome_message, channel_id, embed_data, auto_delete_duration FROM welcome WHERE guild_id = ?", (guild.id,)) as cursor:
                    row = await cursor.fetchone()
            if row is None:
                continue
            welcome_type, welcome_message, channel_id, embed_data, auto_delete_duration = row
            welcome_channel = self.bot.get_channel(channel_id)
            if not welcome_channel:
                continue
            placeholders = {
                "user": member.mention,
                "user_avatar": member.avatar.url if member.avatar else member.default_avatar.url,
                "user_name": member.name,
                "user_id": member.id,
                "user_nick": member.display_name,
                "user_joindate": member.joined_at.strftime("%a, %b %d, %Y"),
                "user_createdate": member.created_at.strftime("%a, %b %d, %Y"),
                "server_name": guild.name,
                "server_id": guild.id,
                "server_membercount": guild.member_count,
                "server_icon": guild.icon.url if guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png",
                "timestamp": discord.utils.format_dt(discord.utils.utcnow())
            }
            try:
                if welcome_type == "simple" and welcome_message:
                    content = await self.safe_format(welcome_message, placeholders)
                    sent_message = await welcome_channel.send(content=content)
                elif welcome_type == "embed" and embed_data:
                    embed_info = json.loads(embed_data)
                    color_value = embed_info.get("color", None)
                    embed_color = 0x2f3136
                    if color_value and isinstance(color_value, str) and color_value.startswith("#"):
                        embed_color = discord.Color(int(color_value.lstrip("#"), 16))
                    elif isinstance(color_value, int):
                        embed_color = discord.Color(color_value)
                    content = await self.safe_format(embed_info.get("message", ""), placeholders) or None
                    embed = discord.Embed(
                        title=await self.safe_format(embed_info.get("title", ""), placeholders),
                        description=await self.safe_format(embed_info.get("description", ""), placeholders),
                        color=embed_color
                    )
                    embed.timestamp = discord.utils.utcnow()
                    if embed_info.get("footer_text"):
                        embed.set_footer(
                            text=await self.safe_format(embed_info["footer_text"], placeholders),
                            icon_url=await self.safe_format(embed_info.get("footer_icon", ""), placeholders)
                        )
                    if embed_info.get("author_name"):
                        embed.set_author(
                            name=await self.safe_format(embed_info["author_name"], placeholders),
                            icon_url=await self.safe_format(embed_info.get("author_icon", ""), placeholders)
                        )
                    if embed_info.get("thumbnail"):
                        embed.set_thumbnail(url=await self.safe_format(embed_info["thumbnail"], placeholders))
                    if embed_info.get("image"):
                        embed.set_image(url=await self.safe_format(embed_info["image"], placeholders))
                    sent_message = await welcome_channel.send(content=content, embed=embed)
                if auto_delete_duration:
                    await sent_message.delete(delay=auto_delete_duration)
            except discord.Forbidden:
                continue
            except discord.HTTPException as e:
                if e.code == 50035 or e.status == 429:
                    await asyncio.sleep(1)
                    self.join_queue[guild.id].append(member)
                    continue
            await asyncio.sleep(2)
        self.processing.remove(guild.id)


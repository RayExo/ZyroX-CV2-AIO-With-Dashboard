# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
# ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
# ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
# ║                                                                  ║
# ║            © 2026 CodeX Devs — All Rights Reserved              ║
# ║                                                                  ║
# ║   discord  ──  https://discord.gg/codexdev                      ║
# ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
# ║   github   ──  https://github.com/RayExo                        ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import discord
from utils.emoji import TICK
from discord.ext import commands
import aiosqlite
import re
from datetime import timedelta
import asyncio

class AntiEmojiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_threshold = 5  

    async def is_automod_enabled(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT enabled FROM automod WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            return result is not None and result[0] == 1

    async def is_anti_emoji_spam_enabled(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT punishment FROM automod_punishments WHERE guild_id = ? AND event = 'Anti emoji spam'", (guild_id,))
            result = await cursor.fetchone()
            return result is not None

    async def get_ignored_channels(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT id FROM automod_ignored WHERE guild_id = ? AND type = 'channel'", (guild_id,))
            return [row[0] for row in await cursor.fetchall()]

    async def get_ignored_roles(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT id FROM automod_ignored WHERE guild_id = ? AND type = 'role'", (guild_id,))
            return [row[0] for row in await cursor.fetchall()]

    async def get_punishment(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT punishment FROM automod_punishments WHERE guild_id = ? AND event = 'Anti emoji spam'", (guild_id,))
            result = await cursor.fetchone()
            return result[0] if result else None

    async def log_action(self, guild, user, channel, action, reason):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT log_channel FROM automod_logging WHERE guild_id = ?", (guild.id,))
            log_channel_id = await cursor.fetchone()

        if log_channel_id and log_channel_id[0]:
            log_channel = guild.get_channel(log_channel_id[0])
            if log_channel:
                embed = discord.Embed(title="Automod Log: Anti Emoji Spam", color=0xFF0000)
                embed.add_field(name="User", value=user.mention, inline=False)
                embed.add_field(name="Action", value=action, inline=False)
                embed.add_field(name="Channel", value=channel.mention, inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.set_footer(text=f"User ID: {user.id}")
                avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
                embed.set_thumbnail(url=avatar_url)
                embed.timestamp=discord.utils.utcnow()
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild = message.guild
        user = message.author
        channel = message.channel
        guild_id = guild.id

        if not await self.is_automod_enabled(guild_id) or not await self.is_anti_emoji_spam_enabled(guild_id):
            return

        if user == guild.owner or user == self.bot.user:
            return

        ignored_channels = await self.get_ignored_channels(guild_id)
        if channel.id in ignored_channels:
            return

        ignored_roles = await self.get_ignored_roles(guild_id)
        if any(role.id in ignored_roles for role in user.roles):
            return

        
        emoji_pattern = re.compile(
            r"<a?:[a-zA-Z0-9_]+:([0-9]+)>|"  #discord emojis
            r"([\U0001F600-\U0001F64F]|"         # Emoticons 
            r"[\U0001F300-\U0001F5FF]|"         # Miscellaneous Symbols and Pictographs
            r"[\U0001F680-\U0001F6FF]|"         # Transport and Map Symbols
            r"[\U0001F700-\U0001F77F]|"         # Alchemical Symbols
            r"[\U0001F780-\U0001F7FF]|"         # Geometric Shapes Extended
            r"[\U0001F800-\U0001F8FF]|"         # Supplemental Arrows-C
            r"[\U0001F900-\U0001F9FF]|"         # Supplemental Symbols and Pictographs
            r"[\U0001FA00-\U0001FAFF]|"         # Chess Symbols
            r"[\U00002700-\U000027BF]|"         # Miscellaneous Symbols
            r"[\U0001F1E6-\U0001F1FF]|"         # Regional Indicator Symbols
            r"[\U0001F004-\U0001F0CF]|"         # Mahjong Tiles and Playing Cards
            r"[\U0001F9B0-\U0001F9FF]"          # Additional Emoji
            r")"
        )
        

       

        emoji_count = len(emoji_pattern.findall(message.content))

        if emoji_count > self.emoji_threshold:
            punishment = await self.get_punishment(guild_id)
            action_taken = None
            reason = f"Emoji Spam ({emoji_count} emojis)"

            try:
                if punishment == "Mute":
                    timeout_duration = discord.utils.utcnow() + timedelta(minutes=1)
                    await user.edit(timed_out_until=timeout_duration, reason=reason)
                    action_taken = "Muted for 1 minute"
                elif punishment == "Kick":
                    await user.kick(reason=reason)
                    action_taken = "Kicked"
                elif punishment == "Ban":
                    await user.ban(reason=reason)
                    action_taken = "Banned"

                await message.delete()
                
                simple_embed = discord.Embed(title="Automod Anti Emoji Spam", color=0xFF0000)
                simple_embed.description = f"{TICK} | {user.mention} has been successfully **{action_taken}** for **Spamming Emojis.**"
                
                simple_embed.set_footer(text="Use the “automod logging” command to get automod logs if it is not enabled.", icon_url=self.bot.user.avatar.url)
                await channel.send(embed=simple_embed, delete_after=30)

                
                await self.log_action(guild, user, channel, action_taken, reason)

            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_rate_limit(self, message):
        await asyncio.sleep(10)


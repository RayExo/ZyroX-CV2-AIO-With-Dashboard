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
from utils.emoji import ZWARNING
from core import zyrox, Cog
from discord.ext import commands
import aiosqlite
from datetime import datetime, timedelta

class AutoBlacklist(Cog):
    def __init__(self, client: zyrox):
        self.client = client
        self.spam_cd_mapping = commands.CooldownMapping.from_cooldown(5, 5, commands.BucketType.member)
        self.spam_command_mapping = commands.CooldownMapping.from_cooldown(6, 10, commands.BucketType.member)
        self.last_spam = {}
        self.spam_threshold = 5
        self.spam_window = timedelta(minutes=10)
        self.db_path = 'db/block.db'
        self.bot_user_id = self.client.user.id if self.client.user else None
        self.guild_command_tracking = {}  

    async def add_to_blacklist(self, user_id=None, guild_id=None, channel=None):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                timestamp = datetime.utcnow()
                if guild_id:
                    await db.execute('''
                        INSERT OR IGNORE INTO guild_blacklist (guild_id, timestamp) VALUES (?, ?)
                    ''', (guild_id, timestamp))
                    if channel:
                        embed = discord.Embed(
                            title=f"{ZWARNING} Guild Blacklisted",
                            description=(
                                f"This guild has been blacklisted due to spamming or automation. "
                                f"If you believe this is a mistake, please contact our [Support Server](https://discord.gg/codexdev) with any proof if possible."
                            ),
                            color=0xFF0000
                        )
                        await channel.send(embed=embed)
                elif user_id:
                    await db.execute('''
                        INSERT OR IGNORE INTO user_blacklist (user_id, timestamp) VALUES (?, ?)
                    ''', (user_id, timestamp))
                await db.commit()
        except aiosqlite.Error as e:
            print(f"Database error: {e}")

    async def check_and_blacklist_guild(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                '''
                SELECT COUNT(DISTINCT user_id) FROM user_blacklist 
                WHERE timestamp >= ?
                ''', 
                (datetime.utcnow() - self.spam_window,)
            ) as cursor:
                count = await cursor.fetchone()
                if count[0] >= self.spam_threshold:
                    async with db.execute('SELECT channel_id FROM guild_settings WHERE guild_id = ?', (guild_id,)) as cursor:
                        channel_id = await cursor.fetchone()
                        if channel_id:
                            channel = self.client.get_channel(channel_id[0])
                            if channel:
                                await self.add_to_blacklist(None, guild_id, channel)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        
        guild_id = message.guild.id if message.guild else None
        if guild_id:
            if guild_id not in self.guild_command_tracking:
                self.guild_command_tracking[guild_id] = []

            
            self.guild_command_tracking[guild_id].append(datetime.utcnow())

            
            self.guild_command_tracking[guild_id] = [
                timestamp for timestamp in self.guild_command_tracking[guild_id] if timestamp >= datetime.utcnow() - timedelta(seconds=2)
            ]

            
            if len(self.guild_command_tracking[guild_id]) > 8:
                
                await self.add_to_blacklist(guild_id=guild_id, channel=message.channel)
                embed = discord.Embed(
                    title=f"{ZWARNING} Guild Blacklisted",
                    description=(
                        f"The guild has been blacklisted for excessive command usage. "
                        f"If you believe this is a mistake, please contact our [Support Server](https://discord.gg/codexdev)."
                    ),
                    color=0xFF0000
                )
                await message.channel.send(embed=embed)
                return

        
        bucket = self.spam_cd_mapping.get_bucket(message)
        retry = bucket.update_rate_limit()

        if retry:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT user_id FROM user_blacklist WHERE user_id = ?', (message.author.id,)) as cursor:
                    if await cursor.fetchone():
                        return

                if message.content in (f'<@{self.bot_user_id}>', f'<@!{self.bot_user_id}>'):
                    await self.add_to_blacklist(user_id=message.author.id)
                    embed = discord.Embed(
                        title=f"{ZWARNING} User Blacklisted",
                        description=f"**{message.author.mention} has been blacklisted for repeatedly mentioning me. If you believe this is a mistake, please contact our [Support Server](https://discord.gg/codexdev) with any proof if possible.**",
                        color=0xFF0000
                    )
                    await message.channel.send(embed=embed)
                    return

                if message.guild:
                    if message.author.id not in self.last_spam:
                        self.last_spam[message.author.id] = []
                    self.last_spam[message.author.id].append(datetime.utcnow())
                    recent_spam = [timestamp for timestamp in self.last_spam.get(message.author.id, []) if timestamp >= datetime.utcnow() - self.spam_window]
                    self.last_spam[message.author.id] = recent_spam
                    if len(recent_spam) >= self.spam_threshold:
                        await self.check_and_blacklist_guild(message.guild.id)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if ctx.author.bot:
            return

        bucket = self.spam_command_mapping.get_bucket(ctx.message)
        retry = bucket.update_rate_limit()

        if retry:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT user_id FROM user_blacklist WHERE user_id = ?', (ctx.author.id,)) as cursor:
                    if await cursor.fetchone():
                        return

                await self.add_to_blacklist(user_id=ctx.author.id)
                embed = discord.Embed(
                    title=f"{ZWARNING} User Blacklisted",
                    description=f"**{ctx.author.mention} has been blacklisted for spamming commands. If you believe this is a mistake, please contact our [Support Server](https://discord.gg/codexdev) with any proof if possible.**",
                    color=0xFF0000
                )
                await ctx.reply(embed=embed)

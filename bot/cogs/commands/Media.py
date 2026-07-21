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
import aiosqlite
from discord.ext import commands
from utils.Tools import blacklist_check, ignore_check
from collections import defaultdict
import time
from utils.cv2 import CV2

class Media(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.infractions = defaultdict(list)
        

    async def set_db(self):
        async with aiosqlite.connect('db/media.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS media_channels (
                    guild_id INTEGER PRIMARY KEY,
                    channel_id INTEGER NOT NULL
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS media_bypass (
                    guild_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')
            await db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.set_db()

    @commands.hybrid_group(name="media", help="Setup Media channel, Media channel will not allow users to send messages other than media files.", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def media(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @media.command(name="setup", aliases=["set", "add"], help="Sets up a media-only channel for the server")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx, *, channel: discord.TextChannel):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT channel_id FROM media_channels WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    await ctx.reply(view=CV2("❌ Error", "A media channel is already set. Please remove it before setting a new one."))
                    return

            await db.execute('INSERT INTO media_channels (guild_id, channel_id) VALUES (?, ?)', (ctx.guild.id, channel.id))
            await db.commit()

        await ctx.reply(view=CV2("✅ Success", f"Successfully set {channel.mention} as the media-only channel.\n\n*Make sure to grant me \"Manage Messages\" permission for functioning of media channel.*"))

    @media.command(name="remove", aliases=["reset", "delete"], help="Removes the current media-only channel")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT channel_id FROM media_channels WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                result = await cursor.fetchone()
                if not result:
                    await ctx.reply(view=CV2("❌ Error", "There is no media-only channel set for this server."))
                    return

            await db.execute('DELETE FROM media_channels WHERE guild_id = ?', (ctx.guild.id,))
            await db.commit()

        await ctx.reply(view=CV2("✅ Success", "Successfully removed the media-only channel."))

    @media.command(name="config", aliases=["settings", "show"], help="Shows the configured media-only channel")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT channel_id FROM media_channels WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                result = await cursor.fetchone()
                if not result:
                    await ctx.reply(view=CV2("❌ Error", "There is no media-only channel set for this server."))
                    return

        channel = self.client.get_channel(result[0])
        await ctx.reply(view=CV2("Media Only Channel", f"The configured media-only channel is {channel.mention}."))

    @media.group(name="bypass", help="Add/Remove user to bypass in Media only channel, Bypassed users can send messages in Media channel.", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def bypass(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @bypass.command(name="add", help="Adds a user to the bypass list")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def bypass_add(self, ctx, user: discord.Member):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT COUNT(*) FROM media_bypass WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                count = await cursor.fetchone()
                if count[0] >= 25:
                    await ctx.reply(view=CV2("❌ Error", "The bypass list can only hold up to 25 users."))
                    return

            async with db.execute('SELECT 1 FROM media_bypass WHERE guild_id = ? AND user_id = ?', (ctx.guild.id, user.id)) as cursor:
                result = await cursor.fetchone()
                if result:
                    await ctx.reply(view=CV2("❌ Error", f"{user.mention} is already in the bypass list."))
                    return

            await db.execute('INSERT INTO media_bypass (guild_id, user_id) VALUES (?, ?)', (ctx.guild.id, user.id))
            await db.commit()

        await ctx.reply(view=CV2("✅ Success", f"{user.mention} has been added to the bypass list."))

    @bypass.command(name="remove", help="Removes a user from the bypass list")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def bypass_remove(self, ctx, user: discord.Member):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT 1 FROM media_bypass WHERE guild_id = ? AND user_id = ?', (ctx.guild.id, user.id)) as cursor:
                result = await cursor.fetchone()
                if not result:
                    await ctx.reply(view=CV2("❌ Error", f"{user.mention} is not in the bypass list."))
                    return

            await db.execute('DELETE FROM media_bypass WHERE guild_id = ? AND user_id = ?', (ctx.guild.id, user.id))
            await db.commit()

        await ctx.reply(view=CV2("✅ Success", f"{user.mention} has been removed from the bypass list."))

    @bypass.command(name="show", aliases=["list", "view"], help="Shows the bypass list")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def bypass_show(self, ctx):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT user_id FROM media_bypass WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                result = await cursor.fetchall()
                if not result:
                    await ctx.reply(view=CV2("Bypass List", "There are no users in the bypass list."))
                    return

        users = [self.client.get_user(user_id).mention for user_id, in result]
        user_mentions = "\n".join(users)

        await ctx.reply(view=CV2("Bypass List", user_mentions))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT channel_id FROM media_channels WHERE guild_id = ?', (message.guild.id,)) as cursor:
                media_channel = await cursor.fetchone()

        if media_channel and message.channel.id == media_channel[0]:
            async with aiosqlite.connect('db/block.db') as block_db:
                async with block_db.execute('SELECT 1 FROM user_blacklist WHERE user_id = ?', (message.author.id,)) as cursor:
                    blacklisted = await cursor.fetchone()

            async with aiosqlite.connect('db/media.db') as db:
                async with db.execute('SELECT 1 FROM media_bypass WHERE guild_id = ? AND user_id = ?', (message.guild.id, message.author.id)) as cursor:
                    bypassed = await cursor.fetchone()

            if blacklisted or bypassed:
                return

            if not message.attachments:
                try:
                    await message.delete()
                    msg = await message.channel.send(view=CV2("⚠️ Warning", f"{message.author.mention} This channel is configured for Media only. Please send only media files."))
                    await msg.delete(delay=5)
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    pass
                except Exception:
                    pass

                current_time = time.time()
                self.infractions[message.author.id].append(current_time)

                
                self.infractions[message.author.id] = [
                    infraction for infraction in self.infractions[message.author.id]
                    if current_time - infraction <= 5
                ]

                if len(self.infractions[message.author.id]) >= 5:  
                    async with aiosqlite.connect('db/block.db') as block_db:
                        await block_db.execute('INSERT OR IGNORE INTO user_blacklist (user_id) VALUES (?)', (message.author.id,))
                        
                        await block_db.commit()

                    desc = (
                        "⚠️ You are blacklisted from using my commands due to spamming in the media channel. "
                        "If you believe this is a mistake, please reach out to the support server with proof."
                    )
                    await message.channel.send(f"{message.author.mention}", view=CV2("You Have Been Blacklisted", desc))
                    del self.infractions[message.author.id]

async def setup(bot):
    await bot.add_cog(Media(bot))

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
from utils.emoji import ARROWRED
from discord.ext import commands
import aiosqlite
from utils.cv2 import CV2

INVITE_DB = "db/invite.db"
EMOJI_INVITE = ARROWRED

from utils.config import BotName

class Tracking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}

    async def ensure_tables(self, guild_id):
        async with aiosqlite.connect(INVITE_DB) as db:
            await db.execute(f'''
                CREATE TABLE IF NOT EXISTS invites_{guild_id} (
                    user_id INTEGER PRIMARY KEY,
                    total INTEGER DEFAULT 0,
                    fake INTEGER DEFAULT 0,
                    left INTEGER DEFAULT 0,
                    rejoin INTEGER DEFAULT 0
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS logging (
                    guild_id INTEGER PRIMARY KEY,
                    channel_id INTEGER
                )
            ''')
            await db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        import asyncio
        async def fetch_invites(guild):
            try:
                self.invites[guild.id] = await guild.invites()
            except discord.Forbidden:
                pass
            except Exception:
                pass

        await asyncio.gather(*(fetch_invites(guild) for guild in self.bot.guilds))

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        try:
            self.invites[invite.guild.id] = await invite.guild.invites()
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        try:
            self.invites[invite.guild.id] = await invite.guild.invites()
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        await self.ensure_tables(guild.id)

        invites_before = self.invites.get(guild.id, [])
        try:
            invites_after = await guild.invites()
        except discord.Forbidden:
            invites_after = []

        inviter = None

        for invite in invites_after:
            for old_invite in invites_before:
                if invite.code == old_invite.code and invite.uses > old_invite.uses:
                    inviter = invite.inviter
                    break
            if inviter:
                break

        self.invites[guild.id] = invites_after

        async with aiosqlite.connect(INVITE_DB) as db:
            if inviter:
                # Check if user has been in DB before (Rejoin)
                async with db.execute(f"SELECT user_id FROM invites_{guild.id} WHERE user_id = ?", (member.id,)) as cursor:
                    user_row = await cursor.fetchone()

                if user_row:
                    await db.execute(f"UPDATE invites_{guild.id} SET rejoin = rejoin + 1 WHERE user_id = ?", (inviter.id,))
                else:
                    await db.execute(f"INSERT OR IGNORE INTO invites_{guild.id} (user_id) VALUES (?)", (inviter.id,))
                    await db.execute(f"UPDATE invites_{guild.id} SET total = total + 1 WHERE user_id = ?", (inviter.id,))
            await db.commit()

            async with db.execute("SELECT channel_id FROM logging WHERE guild_id = ?", (guild.id,)) as cursor:
                log_row = await cursor.fetchone()

        log_channel = guild.get_channel(log_row[0]) if log_row else None
        if log_channel:
            total = await self.get_total_invites(guild.id, inviter.id) if inviter else 0
            msg = (
                f"{member.mention} has joined {guild.name}, invited by "
                f"{inviter.name if inviter else 'Unknown'}, who now has {total} invites."
            )
            await log_channel.send(view=CV2("📥 Member Joined", msg))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        await self.ensure_tables(guild.id)
        async with aiosqlite.connect(INVITE_DB) as db:
            await db.execute(f"UPDATE invites_{guild.id} SET left = left + 1 WHERE user_id = ?", (member.id,))
            await db.commit()

    async def get_total_invites(self, guild_id, user_id):
        async with aiosqlite.connect(INVITE_DB) as db:
            async with db.execute(f"SELECT total FROM invites_{guild_id} WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    @commands.command(aliases=["inv"])
    async def invites(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await self.ensure_tables(ctx.guild.id)

        async with aiosqlite.connect(INVITE_DB) as db:
            async with db.execute(f"SELECT total, fake, left, rejoin FROM invites_{ctx.guild.id} WHERE user_id = ?", (member.id,)) as cursor:
                row = await cursor.fetchone()

        if row:
            total, fake, left, rejoin = row
            real = total - fake - left - rejoin
        else:
            total = fake = left = rejoin = real = 0

        desc = (
            f"{EMOJI_INVITE} **› {member.mention} has `{total}` invites**\n\n"
            f"**Real:** `{real}`\n"
            f"**Fake:** `{fake}`\n"
            f"**Left:** `{left}`\n"
            f"**Rejoins:** `{rejoin}`\n\n"
            f"{EMOJI_INVITE} **Get {BotName} Premium Lifetime [Join Support Here](https://discord.gg/codexdev)**"
        )
        await ctx.send(view=CV2(f"Invite Log - {member.name}", desc))

    @commands.command(aliases=["addinvs"])
    @commands.has_permissions(administrator=True)
    async def addinvites(self, ctx, member: discord.Member, amount: int):
        await self.ensure_tables(ctx.guild.id)
        async with aiosqlite.connect(INVITE_DB) as db:
            await db.execute(f"INSERT OR IGNORE INTO invites_{ctx.guild.id} (user_id) VALUES (?)", (member.id,))
            await db.execute(f"UPDATE invites_{ctx.guild.id} SET total = total + ? WHERE user_id = ?", (amount, member.id))
            await db.commit()
        await ctx.send(view=CV2("✅ Success", f"Added **{amount}** invites to {member.mention}."))

    @commands.command(aliases=["setinvs"])
    @commands.has_permissions(administrator=True)
    async def setinvites(self, ctx, member: discord.Member, amount: int):
        await self.ensure_tables(ctx.guild.id)
        async with aiosqlite.connect(INVITE_DB) as db:
            await db.execute(f"INSERT OR REPLACE INTO invites_{ctx.guild.id} (user_id, total) VALUES (?, ?)", (member.id, amount))
            await db.commit()
        await ctx.send(view=CV2("✅ Success", f"Set invites of {member.mention} to **{amount}**."))

    @commands.command(aliases=["resetinvs"])
    @commands.has_permissions(administrator=True)
    async def resetinvites(self, ctx, member: discord.Member):
        await self.ensure_tables(ctx.guild.id)
        async with aiosqlite.connect(INVITE_DB) as db:
            await db.execute(f"DELETE FROM invites_{ctx.guild.id} WHERE user_id = ?", (member.id,))
            await db.commit()
        await ctx.send(view=CV2("✅ Success", f"Reset invites of {member.mention}."))

    @commands.command(aliases=["invlb"])
    async def invitesleaderboard(self, ctx):
        await self.ensure_tables(ctx.guild.id)
        async with aiosqlite.connect(INVITE_DB) as db:
            async with db.execute(f"SELECT user_id, total FROM invites_{ctx.guild.id} ORDER BY total DESC LIMIT 10") as cursor:
                data = await cursor.fetchall()

        if not data:
            await ctx.send(view=CV2("❌ Error", "No invites found."))
            return

        leaderboard = ""
        for idx, (user_id, total) in enumerate(data, start=1):
            user = ctx.guild.get_member(user_id)
            name = user.name if user else f"Left User ({user_id})"
            leaderboard += f"#{idx} {name} — {total} invites\n"

        await ctx.send(view=CV2("📊 Invite Leaderboard", leaderboard))

    @commands.command(aliases=["invlog"])
    @commands.has_permissions(administrator=True)
    async def invitelogging(self, ctx, channel: discord.TextChannel):
        await self.ensure_tables(ctx.guild.id)
        async with aiosqlite.connect(INVITE_DB) as db:
            await db.execute("INSERT OR REPLACE INTO logging (guild_id, channel_id) VALUES (?, ?)", (ctx.guild.id, channel.id))
            await db.commit()
        await ctx.send(view=CV2("✅ Success", f"Invite logs will now be sent to {channel.mention}"))

async def setup(bot):
    await bot.add_cog(Tracking(bot))
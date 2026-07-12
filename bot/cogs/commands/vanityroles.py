import discord
from discord.ext import commands, tasks
import aiosqlite
import aiohttp
import os
from utils.Tools import *

DB_PATH = "db/vanity.db"

class VanityRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initialize_db())

    async def initialize_db(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS vanity_roles (
                    guild_id INTEGER,
                    vanity TEXT NOT NULL,
                    role_id INTEGER NOT NULL,
                    log_channel_id INTEGER NOT NULL,
                    current_status TEXT,
                    PRIMARY KEY (guild_id, vanity)
                )
            """)
            await db.commit()

            async with db.execute("PRAGMA table_info(vanity_roles)") as cursor:
                columns = await cursor.fetchall()
                column_names = [column[1] for column in columns]

            if "current_status" not in column_names:
                await db.execute("ALTER TABLE vanity_roles ADD COLUMN current_status TEXT")
                await db.commit()

    @commands.group(name="vanityroles", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    async def vanityroles(self, ctx):
        await ctx.send("❗ Usage: `vanityroles setup <vanity> <@role> <#channel>`, `vanityroles show`, `vanityroles reset`")

    @vanityroles.command(name="setup")
    @blacklist_check()
    @ignore_check()
    async def setup(self, ctx, vanity: str, role: discord.Role, channel: discord.TextChannel):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT OR REPLACE INTO vanity_roles (guild_id, vanity, role_id, log_channel_id, current_status)
                VALUES (?, ?, ?, ?, NULL)
            """, (ctx.guild.id, vanity.lower(), role.id, channel.id))
            await db.commit()
        embed = discord.Embed(
            title="✅ Vanity Role Setup",
            description=f"Vanity: `{vanity}`\nRole: {role.mention}\nLog Channel: {channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @vanityroles.command(name="show")
    @blacklist_check()
    @ignore_check()
    async def show(self, ctx):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT vanity, role_id, log_channel_id FROM vanity_roles WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            return await ctx.send("❌ No vanity role setups found.")

        embed = discord.Embed(title="🔧 Vanity Role Settings", color=discord.Color.blue())
        for vanity, role_id, log_channel_id in rows:
            role = ctx.guild.get_role(role_id)
            channel = ctx.guild.get_channel(log_channel_id)
            embed.add_field(
                name=f"Vanity: `{vanity}`",
                value=f"Role: {role.mention if role else role_id}\nLog: {channel.mention if channel else log_channel_id}",
                inline=False
            )
        await ctx.send(embed=embed)

    @vanityroles.command(name="reset")
    @blacklist_check()
    @ignore_check()
    async def reset(self, ctx):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM vanity_roles WHERE guild_id = ?", (ctx.guild.id,))
            await db.commit()
        await ctx.send("✅ All vanity role configurations have been reset.")

    @tasks.loop(seconds=15)
    async def vanity_checker(self):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT guild_id, vanity, role_id, log_channel_id, current_status FROM vanity_roles") as cursor:
                rows = await cursor.fetchall()

        for guild_id, vanity, role_id, log_channel_id, current_status in rows:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue

            role = guild.get_role(role_id)
            log_channel = guild.get_channel(log_channel_id)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://discord.com/api/v10/invites/{vanity}") as response:
                        is_active = response.status == 200
            except Exception as e:
                print(f"⚠️ Error checking vanity {vanity}: {e}")
                continue

            # Vanity is ACTIVE
            if is_active and current_status != "active":
                await self.update_status(guild_id, vanity, "active")
                assigned = 0
                for member in guild.members:
                    if role and role not in member.roles:
                        try:
                            await member.add_roles(role, reason="Vanity active")
                            assigned += 1
                        except Exception as e:
                            print(f"❌ Could not add role to {member}: {e}")
                if log_channel:
                    await log_channel.send(f"✅ Vanity `{vanity}` is now **active**. Role assigned to {assigned} members.")

            # Vanity is INACTIVE
            elif not is_active and current_status == "active":
                await self.update_status(guild_id, vanity, None)
                removed = 0
                for member in guild.members:
                    if role and role in member.roles:
                        try:
                            await member.remove_roles(role, reason="Vanity inactive")
                            removed += 1
                        except Exception as e:
                            print(f"❌ Could not remove role from {member}: {e}")
                if log_channel:
                    await log_channel.send(f"❌ Vanity `{vanity}` is now **inactive**. Role removed from {removed} members.")

    async def update_status(self, guild_id, vanity, new_status):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                UPDATE vanity_roles SET current_status = ? WHERE guild_id = ? AND vanity = ?
            """, (new_status, guild_id, vanity))
            await db.commit()

    @vanity_checker.before_loop
    async def before_checker(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    cog = VanityRoles(bot)
    await bot.add_cog(cog)
    cog.vanity_checker.start()
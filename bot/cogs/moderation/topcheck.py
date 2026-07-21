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
from utils.emoji import CROSS, TICK
from discord.ext import commands
import aiosqlite
import asyncio
from utils.config import *

class TopCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "db/topcheck.db"
        self.bot.loop.create_task(self.setup())

    async def setup(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS topcheck (
                    guild_id INTEGER PRIMARY KEY,
                    enabled INTEGER
                )
            """)
            await db.commit()

    async def is_topcheck_enabled(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT enabled FROM topcheck WHERE guild_id = ?", (guild_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0] == 1
                return False

    async def enable_topcheck(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO topcheck (guild_id, enabled) VALUES (?, 1)", (guild_id,))
            await db.commit()

    async def disable_topcheck(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE topcheck SET enabled = 0 WHERE guild_id = ?", (guild_id,))
            await db.commit()

    @commands.group(
        name="topcheck",
        help="Manage topcheck settings for the server.",
        invoke_without_command=True)
    @commands.guild_only()
    async def topcheck(self, ctx):
        embed = discord.Embed(title="Top Check System",
                              description=(
        "This system ensures that the bot’s role is positioned higher than the user’s top role before executing specific commands.\n\n"
        f"When topcheck is enabled, only users with roles above the bot's ({BRAND_NAME}) role can perform certain moderation actions. "
        "If topcheck is disabled, any user with the required permissions for a command can execute it.\n\n"
        "**Moderation actions affected by topcheck:**\n"
        "- BAN\n"
        "- KICK\n"
        "- ROLE DELETE\n"
        "- ROLE CREATE\n"
        "- MEMBER UPDATE\n\n"
        "__**Subcommands:**__\n"
        f"• `{ctx.prefix}topcheck enable` - Enables top check for the server.\n"
        f"• `{ctx.prefix}topcheck disable` - Disables top check for the server."
    ),
                              color=0xFF0000)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @topcheck.command(
        name="enable",
        help="Enable topcheck for the guild")
    @commands.guild_only()
    async def topcheck_enable(self, ctx):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.reply(f"{CROSS} Only the **Server Owner** can enable topcheck.")
        if await self.is_topcheck_enabled(ctx.guild.id):
            return await ctx.reply(f"{CROSS} Topcheck is already enabled for this server.")
        await self.enable_topcheck(ctx.guild.id)
        await ctx.reply(f"{TICK} Topcheck has been Successfully enabled for this server.")

    @topcheck.command(
        name="disable",
        help="Disable topcheck for the guild")
    @commands.guild_only()
    async def topcheck_disable(self, ctx):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.reply("Only the **Server Owner** can disable topcheck.")
        if not await self.is_topcheck_enabled(ctx.guild.id):
            return await ctx.reply(f"{CROSS} Topcheck is not enabled for this server.")
        await self.disable_topcheck(ctx.guild.id)
        await ctx.reply(f"{TICK} Topcheck has been Successfully disabled for this server.")

 
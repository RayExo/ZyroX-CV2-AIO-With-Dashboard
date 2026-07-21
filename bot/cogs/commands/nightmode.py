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
from discord.ext import commands
import aiosqlite
import os
from utils.Tools import *
from utils.cv2 import CV2
from discord.ui import TextDisplay, Separator, ActionRow, LayoutView, Container
from utils.config import OWNER_IDS_STR

# Database setup
db_folder = "db"
db_file = "anti.db"
db_path = os.path.join(db_folder, db_file)


class Nightmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initialize_db())
        self.ricky = OWNER_IDS_STR
        self.color = 0xFF0000

    async def initialize_db(self):
        self.db = await aiosqlite.connect(db_path)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS Nightmode (
                guildId TEXT,
                roleId TEXT,
                adminPermissions INTEGER
            )
        """)
        await self.db.commit()

    async def is_extra_owner(self, user, guild):
        async with self.db.execute(
            """
            SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?
        """,
            (guild.id, user.id),
        ) as cursor:
            extra_owner = await cursor.fetchone()
        return extra_owner is not None

    @commands.hybrid_group(
        name="nightmode",
        aliases=[],
        help="Manages Nightmode feature",
        invoke_without_command=True,
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def nightmode(self, ctx):
        view = CV2(
            "__**Nightmode**__",
            "Nightmode swiftly disables dangerous permissions for roles, like stripping `ADMINISTRATION` rights, while preserving original settings for seamless restoration.\n\n**Make sure to keep my ROLE above all roles you want to protect.**",
            "**Usage**\n `nightmode enable`\n `nightmode disable`",
        )
        await ctx.send(view=view)

    @nightmode.command(name="enable", help="Enable nightmode")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def enable_nightmode(self, ctx):
        if ctx.guild.member_count < 50:
            view = CV2(
                "Access Denied",
                "Your Server Doesn't Meet My 50 Member Criteria",
            )
            return await ctx.send(view=view)

        own = ctx.author.id == ctx.guild.owner_id
        check = await self.is_extra_owner(ctx.author, ctx.guild)
        if not own and not check and ctx.author.id not in self.ricky:
            view = CV2(
                "Access Denied",
                "Only Server Owner Or Extraowner Can Run This Command.!",
            )
            return await ctx.send(view=view)

        if (
            not own
            and not (ctx.guild.me.top_role.position <= ctx.author.top_role.position)
            and ctx.author.id not in self.ricky
        ):
            view = CV2(
                "Access Denied",
                "Only Server Owner or Extraowner Having **Higher role than me can run this command**",
            )
            return await ctx.send(view=view)

        bot_highest_role = ctx.guild.me.top_role
        manageable_roles = [
            role
            for role in ctx.guild.roles
            if role.position < bot_highest_role.position
            and role.name != "@everyone"
            and role.permissions.administrator
            and not role.managed
        ]

        if not manageable_roles:
            view = CV2(
                "Error",
                "No Roles Found With Admin Permissions",
            )
            return await ctx.send(view=view)

        async with self.db.execute(
            "SELECT guildId FROM Nightmode WHERE guildId = ?", (str(ctx.guild.id),)
        ) as cursor:
            if await cursor.fetchone():
                view = CV2(
                    "Error",
                    "Nightmode is already enabled.",
                )
                return await ctx.send(view=view)

        async with self.db.cursor() as cursor:
            for role in manageable_roles:
                admin_permissions = discord.Permissions(administrator=True)
                if role.permissions.administrator:
                    permissions = role.permissions
                    permissions.administrator = False

                    await role.edit(permissions=permissions, reason="Nightmode ENABLED")

                    await cursor.execute(
                        """
                    INSERT OR REPLACE INTO Nightmode (guildId, roleId, adminPermissions)
                    VALUES (?, ?, ?)
                    """,
                        (str(ctx.guild.id), str(role.id), int(admin_permissions.value)),
                    )
            await self.db.commit()

        view = CV2(
            "Success",
            "Nightmode enabled! Dangerous Permissions Disabled For Manageable Roles.",
        )
        await ctx.send(view=view)

    @nightmode.command(name="disable", help="Disable nightmode")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def disable_nightmode(self, ctx):
        if ctx.guild.member_count < 50:
            view = CV2(
                "Access Denied",
                "Your Server Doesn't Meet My 50 Member Criteria",
            )
            return await ctx.send(view=view)

        own = ctx.author.id == ctx.guild.owner_id
        check = await self.is_extra_owner(ctx.author, ctx.guild)
        if not own and not check and ctx.author.id not in self.ricky:
            view = CV2(
                "Access Denied",
                "Only Server Owner Or Extraowner Can Run This Command.!",
            )
            return await ctx.send(view=view)

        if (
            not own
            and not (ctx.guild.me.top_role.position <= ctx.author.top_role.position)
            and ctx.author.id not in self.ricky
        ):
            view = CV2(
                "Access Denied",
                "Only Server Owner or Extraowner Having **Higher role than me can run this command**",
            )
            return await ctx.send(view=view)

        async with self.db.execute(
            "SELECT roleId, adminPermissions FROM Nightmode WHERE guildId = ?",
            (str(ctx.guild.id),),
        ) as cursor:
            stored_roles = await cursor.fetchall()

        if not stored_roles:
            view = CV2(
                "Error",
                "Nightmode is not enabled.",
            )
            return await ctx.send(view=view)

        async with self.db.cursor() as cursor:
            for role_id, admin_permissions in stored_roles:
                role = ctx.guild.get_role(int(role_id))
                if role:
                    permissions = discord.Permissions(
                        administrator=bool(admin_permissions)
                    )
                    await role.edit(
                        permissions=permissions, reason="Nightmode DISABLED"
                    )

                    await cursor.execute(
                        "DELETE FROM Nightmode WHERE guildId = ? AND roleId = ?",
                        (str(ctx.guild.id), role_id),
                    )
            await self.db.commit()

        view = CV2(
            "Success",
            "Nightmode disabled! Restored Permissions For Manageable Roles.",
        )
        await ctx.send(view=view)

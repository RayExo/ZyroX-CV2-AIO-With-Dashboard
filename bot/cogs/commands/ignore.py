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

from __future__ import annotations
import discord
from utils.emoji import CROSS, TICK, ZWARNING
from discord.ui import LayoutView, TextDisplay, Separator, Container
from discord.ext import commands
from core import *
from utils.Tools import *
from typing import Optional
import aiosqlite

color = 0xFF0000


class SuccessView(LayoutView):
    def __init__(self, title, description):
        super().__init__(timeout=None)
        self.add_item(
            Container(
                TextDisplay(f"**{TICK} {title}**"),
                Separator(visible=True),
                TextDisplay(description),
            )
        )


class ErrorView(LayoutView):
    def __init__(self, title, description):
        super().__init__(timeout=None)
        self.add_item(
            Container(
                TextDisplay(f"**{CROSS} {title}**"),
                Separator(visible=True),
                TextDisplay(description),
            )
        )


class WarningView(LayoutView):
    def __init__(self, title, description):
        super().__init__(timeout=None)
        self.add_item(
            Container(
                TextDisplay(f"**{ZWARNING} {title}**"),
                Separator(visible=True),
                TextDisplay(description),
            )
        )


class ListView(LayoutView):
    def __init__(self, title, items, empty_message, guild=None):
        super().__init__(timeout=None)

        if not items:
            self.add_item(
                Container(
                    TextDisplay(f"**{title}**"),
                    Separator(visible=True),
                    TextDisplay(empty_message),
                )
            )
        else:
            if guild:
                mentions = []
                for item in items:
                    if isinstance(item, int):
                        entity = guild.get_channel(item) or guild.get_member(item)
                        mentions.append(entity.mention if entity else f"ID {item}")
                    else:
                        mentions.append(f"`{item}`")
                description = "\n".join(mentions)
            else:
                description = "\n".join([f"`{item}`" for item in items])

            self.add_item(
                Container(
                    TextDisplay(f"**{title}**"),
                    Separator(visible=True),
                    TextDisplay(description),
                )
            )


class Ignore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "db/ignore.db"
        self.color = 0xFF0000
        bot.loop.create_task(self.initialize_db())

    async def initialize_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS ignored_commands (guild_id INTEGER, command_name TEXT)"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS ignored_channels (guild_id INTEGER, channel_id INTEGER)"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS ignored_users (guild_id INTEGER, user_id INTEGER)"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS bypassed_users (guild_id INTEGER, user_id INTEGER)"
            )
            await db.commit()

    @commands.group(
        name="ignore",
        help="Manage ignored commands, channels, users, and bypassed users.",
        invoke_without_command=True,
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _ignore(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_ignore.group(
        name="command",
        help="Manage ignored commands in this guild.",
        invoke_without_command=True,
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _command(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_command.command(name="add", help="Adds a command to the ignore list.")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def command_add(self, ctx: commands.Context, command_name: str):
        command_name_normalized = command_name.strip().lower()
        command = self.bot.get_command(command_name_normalized)
        if not command:
            await ctx.reply(
                view=ErrorView("Error", f"`{command_name}` is not a valid command.")
            )
            return

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM ignored_commands WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            count = await cursor.fetchone()
            if count[0] >= 25:
                await ctx.reply(
                    view=WarningView(
                        "Access Denied",
                        "You can only add up to 25 commands to the ignore list.",
                    )
                )
                return

            cursor = await db.execute(
                "SELECT command_name FROM ignored_commands WHERE guild_id = ? AND command_name = ?",
                (ctx.guild.id, command_name_normalized),
            )
            result = await cursor.fetchone()
            if result:
                await ctx.reply(
                    view=ErrorView(
                        "Error",
                        f"`{command_name}` is already in the ignore commands list.",
                    )
                )
            else:
                await db.execute(
                    "INSERT INTO ignored_commands (guild_id, command_name) VALUES (?, ?)",
                    (ctx.guild.id, command_name_normalized),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Success",
                        f"Successfully added `{command_name}` to the ignore commands list.",
                    )
                )

    @_command.command(name="remove", help="Removes a command from the ignore list.")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def command_remove(self, ctx: commands.Context, command_name: str):
        command_name_normalized = command_name.strip().lower()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT command_name FROM ignored_commands WHERE guild_id = ? AND command_name = ?",
                (ctx.guild.id, command_name_normalized),
            )
            result = await cursor.fetchone()
            if not result:
                await ctx.reply(
                    view=ErrorView(
                        "Error", f"`{command_name}` is not in the ignore commands list."
                    )
                )
            else:
                await db.execute(
                    "DELETE FROM ignored_commands WHERE guild_id = ? AND command_name = ?",
                    (ctx.guild.id, command_name_normalized),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Success",
                        f"Successfully removed `{command_name}` from the ignore commands list.",
                    )
                )

    @_command.command(name="show", help="Displays the list of ignored commands.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def command_show(self, ctx: commands.Context):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT command_name FROM ignored_commands WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            commands = await cursor.fetchall()
            if not commands:
                await ctx.reply(
                    view=ListView(
                        "Ignored Commands",
                        [],
                        "No commands are currently ignored in this server.",
                    )
                )
            else:
                await ctx.reply(
                    view=ListView("Ignored Commands", [c[0] for c in commands], "")
                )

    @_ignore.group(
        name="channel",
        help="Manage ignored channels in this guild.",
        invoke_without_command=True,
    )
    @blacklist_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _channel(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_channel.command(name="add", help="Adds a channel to the ignore list.")
    @blacklist_check()
    @commands.has_permissions(administrator=True)
    async def channel_add(self, ctx: commands.Context, channel: discord.TextChannel):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM ignored_channels WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            count = await cursor.fetchone()

            if count[0] >= 30:
                await ctx.reply(
                    view=WarningView(
                        "Access Denied",
                        "You can only add up to 30 channels to the ignore list.",
                    )
                )
                return

            cursor = await db.execute(
                "SELECT channel_id FROM ignored_channels WHERE guild_id = ? AND channel_id = ?",
                (ctx.guild.id, channel.id),
            )
            result = await cursor.fetchone()

            if result:
                await ctx.reply(
                    view=ErrorView(
                        "Error",
                        f"{channel.mention} is already in the ignore channels list.",
                    )
                )
            else:
                await db.execute(
                    "INSERT INTO ignored_channels (guild_id, channel_id) VALUES (?, ?)",
                    (ctx.guild.id, channel.id),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Success",
                        f"Successfully added {channel.mention} to the ignore channels list.",
                    )
                )

    @_channel.command(name="remove", help="Removes a channel from the ignore list.")
    @blacklist_check()
    @commands.has_permissions(administrator=True)
    async def channel_remove(self, ctx: commands.Context, channel: discord.TextChannel):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT channel_id FROM ignored_channels WHERE guild_id = ? AND channel_id = ?",
                (ctx.guild.id, channel.id),
            )
            result = await cursor.fetchone()

            if not result:
                await ctx.reply(
                    view=ErrorView(
                        "Error",
                        f"{channel.mention} is not in the ignore channels list.",
                    )
                )
            else:
                await db.execute(
                    "DELETE FROM ignored_channels WHERE guild_id = ? AND channel_id = ?",
                    (ctx.guild.id, channel.id),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Success",
                        f"Successfully removed {channel.mention} from the ignore channels list.",
                    )
                )

    @_channel.command(name="show", help="Displays the list of ignored channels.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def channel_show(self, ctx: commands.Context):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT channel_id FROM ignored_channels WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            channels = await cursor.fetchall()

            if not channels:
                await ctx.reply(
                    view=ListView(
                        "Ignored Channels",
                        [],
                        "No channels are currently ignored in this server.",
                    )
                )
            else:
                await ctx.reply(
                    view=ListView(
                        "Ignored Channels", [c[0] for c in channels], "", ctx.guild
                    )
                )

    @_ignore.group(
        name="user",
        help="Manage ignored users in this guild.",
        invoke_without_command=True,
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _user(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_user.command(name="add", help="Adds a user to the ignore list.")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def user_add(self, ctx: commands.Context, user: discord.User):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM ignored_users WHERE guild_id = ?", (ctx.guild.id,)
            )
            count = await cursor.fetchone()

            if count[0] >= 30:
                await ctx.reply(
                    view=WarningView(
                        "Access Denied",
                        "You can only add up to 30 users to the ignore list.",
                    )
                )
                return

            cursor = await db.execute(
                "SELECT user_id FROM ignored_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, user.id),
            )
            result = await cursor.fetchone()

            if result:
                await ctx.reply(
                    view=ErrorView(
                        "Error", f"{user.mention} is already in the ignore users list."
                    )
                )
            else:
                await db.execute(
                    "INSERT INTO ignored_users (guild_id, user_id) VALUES (?, ?)",
                    (ctx.guild.id, user.id),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Success",
                        f"Successfully added {user.mention} to the ignore users list.",
                    )
                )

    @_user.command(name="remove", help="Removes a user from the ignore list.")
    @blacklist_check()
    @commands.has_permissions(administrator=True)
    async def user_remove(self, ctx: commands.Context, user: discord.User):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM ignored_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, user.id),
            )
            result = await cursor.fetchone()

            if not result:
                await ctx.reply(
                    view=ErrorView(
                        "Error", f"{user.mention} is not in the ignore users list."
                    )
                )
            else:
                await db.execute(
                    "DELETE FROM ignored_users WHERE guild_id = ? AND user_id = ?",
                    (ctx.guild.id, user.id),
                )
                await db.commit()
                await ctx.send(
                    view=SuccessView(
                        "Success",
                        f"Successfully removed {user.mention} from the ignore users list.",
                    )
                )

    @_user.command(name="show", help="Displays the list of ignored users.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def user_show(self, ctx: commands.Context):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM ignored_users WHERE guild_id = ?", (ctx.guild.id,)
            )
            users = await cursor.fetchall()

            if not users:
                await ctx.reply(
                    view=ListView(
                        "Ignored Users",
                        [],
                        "No users are currently ignored in this server.",
                    )
                )
            else:
                await ctx.reply(
                    view=ListView("Ignored Users", [u[0] for u in users], "", ctx.guild)
                )

    @_ignore.group(
        name="bypass",
        help="Manage bypassed users in this guild.",
        invoke_without_command=True,
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _bypass(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_bypass.command(name="add", help="Adds a user to the bypass list.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def bypass_add(self, ctx: commands.Context, user: discord.User):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM bypassed_users WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            count = await cursor.fetchone()

            if count[0] >= 30:
                await ctx.reply(
                    view=WarningView(
                        "Access Denied",
                        "You can only add up to 30 users to the bypass list.",
                    )
                )
                return

            cursor = await db.execute(
                "SELECT user_id FROM bypassed_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, user.id),
            )
            result = await cursor.fetchone()

            if result:
                await ctx.reply(
                    view=ErrorView(
                        "Error", f"{user.mention} is already in the bypass users list."
                    )
                )
            else:
                await db.execute(
                    "INSERT INTO bypassed_users (guild_id, user_id) VALUES (?, ?)",
                    (ctx.guild.id, user.id),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Success",
                        f"Successfully added {user.mention} to the bypass users list.",
                    )
                )

    @_bypass.command(name="remove", help="Removes a user from the bypass list.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def bypass_remove(self, ctx: commands.Context, user: discord.User):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM bypassed_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, user.id),
            )
            result = await cursor.fetchone()

            if not result:
                await ctx.reply(
                    view=ErrorView(
                        "Error", f"{user.mention} is not in the bypass users list."
                    )
                )
            else:
                await db.execute(
                    "DELETE FROM bypassed_users WHERE guild_id = ? AND user_id = ?",
                    (ctx.guild.id, user.id),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Success",
                        f"Successfully removed {user.mention} from the bypass users list.",
                    )
                )

    @_bypass.command(
        name="show", aliases=["list"], help="Displays the list of bypassed users."
    )
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def bypass_show(self, ctx: commands.Context):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM bypassed_users WHERE guild_id = ?", (ctx.guild.id,)
            )
            users = await cursor.fetchall()

            if not users:
                await ctx.reply(
                    view=ListView(
                        "Bypassed Users",
                        [],
                        "No users are currently bypassed in this server.",
                    )
                )
            else:
                await ctx.reply(
                    view=ListView(
                        "Bypassed Users", [u[0] for u in users], "", ctx.guild
                    )
                )

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
from utils.Tools import *
from utils.cv2 import CV2


class NotifCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "db/notify.db"
        self.loop_task = self.bot.loop.create_task(self.setup_db())

    async def setup_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS notifications (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                type TEXT NOT NULL UNIQUE,
                                role_id INTEGER NOT NULL,
                                channel_id INTEGER NOT NULL)""")
            await db.commit()

    @commands.group(invoke_without_command=True)
    async def setnotif(self, ctx):
        view = CV2(
            "Notification Commands",
            "Subcommands: twitch, youtube, list, reset",
        )
        await ctx.send(view=view)

    @setnotif.command()
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def twitch(self, ctx, role: discord.Role, channel: discord.TextChannel):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM notifications WHERE type = ?", ("twitch",)
            ) as existing:
                row = await existing.fetchone()
                if row:
                    view = CV2(
                        "Access Denied",
                        "Twitch notification already set. Remove it first.",
                    )
                    await ctx.reply(view=view)
                    return

            await db.execute(
                "INSERT INTO notifications (type, role_id, channel_id) VALUES (?, ?, ?)",
                ("twitch", role.id, channel.id),
            )
            await db.commit()
            view = CV2(
                "Success",
                f"Twitch notifications set for {role.mention} in {channel.mention}.",
            )
            await ctx.reply(view=view)

    @setnotif.command()
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def youtube(self, ctx, role: discord.Role, channel: discord.TextChannel):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM notifications WHERE type = ?", ("youtube",)
            ) as existing:
                row = await existing.fetchone()
                if row:
                    view = CV2(
                        "Access Denied",
                        "YouTube notification already set. Remove it first.",
                    )
                    await ctx.reply(view=view)
                    return

            await db.execute(
                "INSERT INTO notifications (type, role_id, channel_id) VALUES (?, ?, ?)",
                ("youtube", role.id, channel.id),
            )
            await db.commit()
            view = CV2(
                "Success",
                f"YouTube notifications set for {role.mention} in {channel.mention}.",
            )
            await ctx.reply(view=view)

    @setnotif.command()
    async def list(self, ctx):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM notifications") as cursor:
                rows = await cursor.fetchall()
                if not rows:
                    view = CV2(
                        "Notification Settings",
                        "No Twitch and YouTube notification channels set.",
                    )
                    await ctx.reply(view=view)
                    return

            lines = []
            for row in rows:
                notif_type = row[1].capitalize()
                role = ctx.guild.get_role(row[2])
                channel = ctx.guild.get_channel(row[3])
                if role and channel:
                    lines.append(
                        f"**{notif_type} Notifications**\nRole: {role.mention} | Channel: {channel.mention}"
                    )
                else:
                    lines.append(
                        f"**{notif_type} Notifications**\nRole or Channel not found"
                    )

            view = CV2(
                "Current Notification Settings",
                *lines,
            )
            await ctx.reply(view=view)

    @setnotif.command()
    async def reset(self, ctx):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM notifications WHERE type IN (?, ?)", ("twitch", "youtube")
            )
            await db.commit()
            view = CV2(
                "Success",
                "Twitch and YouTube notifications have been reset.",
            )
            await ctx.send(view=view)

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):

        streaming = next(
            (
                activity
                for activity in after.activities
                if isinstance(activity, discord.Streaming)
            ),
            None,
        )

        if streaming:
            stream_type = (
                "twitch"
                if "twitch" in streaming.url.lower()
                else "youtube"
                if "youtube" in streaming.url.lower()
                else None
            )
            if stream_type:
                async with aiosqlite.connect(self.db_path) as db:
                    async with db.execute(
                        "SELECT role_id, channel_id FROM notifications WHERE type = ?",
                        (stream_type,),
                    ) as cursor:
                        row = await cursor.fetchone()
                        if row:
                            role_id, channel_id = row
                            role = after.guild.get_role(role_id)
                            channel = after.guild.get_channel(channel_id)

                            if role and channel:
                                embed = discord.Embed(
                                    title=f"{after.display_name} is now live!",
                                    description=f"{after.mention} is now streaming on {stream_type.capitalize()}.",
                                    color=0xFF0000,
                                )
                                embed.add_field(
                                    name="Stream Title",
                                    value=streaming.name,
                                    inline=False,
                                )
                                embed.add_field(
                                    name="Watch here", value=streaming.url, inline=False
                                )
                                await channel.send(content=role.mention, embed=embed)

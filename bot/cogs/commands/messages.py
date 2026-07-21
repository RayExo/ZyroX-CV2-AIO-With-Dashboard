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
from discord.ui import LayoutView, TextDisplay, Separator, Container
from discord.ext import commands
import sqlite3
from datetime import datetime
from utils.config import *


class MessagesView(LayoutView):
    def __init__(self, member, total, today_count, daily_average, author):
        super().__init__(timeout=None)

        self.add_item(
            Container(
                TextDisplay(f"**Messages Stats for {member.display_name}**"),
                Separator(visible=True),
                TextDisplay(
                    f"**User**: {member.mention}\n\n"
                    f"**Daily Messages**: {daily_average}\n"
                    f"**Today Messages**: {today_count}\n"
                    f"**Total Messages**: {total}\n\n"
                    f"**{ARROWRED}Upgrade Your Experience With [{BRAND_NAME} Noprefix](https://discord.gg/codexdev)**"
                ),
            )
        )


class Messages(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        conn = sqlite3.connect("db/messages.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                guild_id INTEGER,
                user_id INTEGER,
                date TEXT,
                count INTEGER
            )
        """)

        today = datetime.utcnow().strftime("%Y-%m-%d")
        c.execute(
            "SELECT count FROM messages WHERE guild_id = ? AND user_id = ? AND date = ?",
            (message.guild.id, message.author.id, today),
        )
        result = c.fetchone()

        if result:
            c.execute(
                "UPDATE messages SET count = count + 1 WHERE guild_id = ? AND user_id = ? AND date = ?",
                (message.guild.id, message.author.id, today),
            )
        else:
            c.execute(
                "INSERT INTO messages (guild_id, user_id, date, count) VALUES (?, ?, ?, 1)",
                (message.guild.id, message.author.id, today),
            )

        conn.commit()
        conn.close()

    @commands.command(name="messages", aliases=["msg"])
    async def messages(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        today = datetime.utcnow().strftime("%Y-%m-%d")

        conn = sqlite3.connect("db/messages.db")
        c = conn.cursor()
        c.execute(
            "SELECT date, count FROM messages WHERE guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id),
        )
        data = c.fetchall()
        conn.close()

        total = sum(row[1] for row in data)
        today_count = sum(row[1] for row in data if row[0] == today)
        unique_days = set(row[0] for row in data)
        daily_average = round(total / len(unique_days), 2) if unique_days else 0

        view = MessagesView(member, total, today_count, daily_average, ctx.author)
        await ctx.send(view=view)


async def setup(client):
    await client.add_cog(Messages(client))

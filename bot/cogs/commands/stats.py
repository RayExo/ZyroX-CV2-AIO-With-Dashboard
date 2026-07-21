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
from utils.emoji import CODEBASE, LOADING, SYSTEM, THUNDER, ZYROX_CODE, ZYROX_COMMAND, ZYROX_GLOBAL, ZYROX_OWNER, ZYROX_SEARCH
import psutil
import sys
import os
import time
import aiosqlite
import datetime
from discord.ui import LayoutView, TextDisplay, Separator, Container, ActionRow, Select
from discord.ext import commands
from utils.Tools import *
import wavelink
from utils.config import *


def analyze_codebase(path="."):
    total_files = total_lines = total_words = 0
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(
                (".py", ".js", ".json", ".ts", ".html", ".css", ".env", ".txt")
            ):
                total_files += 1
                try:
                    with open(
                        os.path.join(root, file), "r", encoding="utf-8", errors="ignore"
                    ) as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                        total_words += sum(len(line.split()) for line in lines)
                except:
                    continue
    return total_files, total_lines, total_words


def create_stats_content(stats_data, selected):
    content_map = {
        "Quick Overview": (
            f"**{THUNDER} Quick Overview**\n\n"
            f"**Servers**: {stats_data['guilds']}\n"
            f"**Users**: {stats_data['users']}\n"
            f"**Uptime**: {stats_data['uptime']}\n\n"
            f"_Use the dropdown to view more stats._"
        ),
        "System Info": (
            f"**{SYSTEM} Hardware**\n"
            f"Cpu Usage: **{stats_data['cpu']}%**\n"
            f"Ram Usage: **{stats_data['ram']}%**\n\n"
            f"**{ZYROX_CODE} Software**\n"
            f"Python: **{sys.version_info.major}.{sys.version_info.minor}**\n"
            f"Discord.py: **{discord.__version__}**"
        ),
        "General Info": (
            f"**Uptime**: `{stats_data['uptime']}`\n\n"
            f"**{ZYROX_GLOBAL} Server Stats**\n"
            f"Guilds: **{stats_data['guilds']}**\n"
            f"Users: **{stats_data['users']}**\n\n"
            f"**{ZYROX_COMMAND} Commands Stats**\n"
            f"Total Commands: **{stats_data['all_cmds']}**\n"
            f"Slash Commands: **{stats_data['slash_cmds']}**"
        ),
        "Team Info": (
            "There is only one person who made me. Thanks to him ❤️.\n\n"
            f"**{ZYROX_OWNER} Main Owner**\n"
            "[01]. [runxking](https://discord.com/users/767979794411028491)\n"
            "[02]. [Ray](https://discord.com/users/870179991462236170)"
        ),
        "Code Info": (
            f"**{ZYROX_SEARCH} Codebase Overview**\n\n"
            f"Files: **{stats_data['files']}**\n"
            f"Lines: **{stats_data['lines']}**\n"
            f"Words: **{stats_data['words']}**"
        ),
    }
    return content_map.get(selected, "")


class StatsView(LayoutView):
    def __init__(self, ctx, stats_data):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.stats_data = stats_data

        self.select = Select(
            placeholder=f"{BRAND_NAME} Statistics",
            options=[
                discord.SelectOption(
                    label="Quick Overview",
                    emoji=THUNDER,
                    description="Quick stats overview",
                ),
                discord.SelectOption(
                    label="System Info",
                    emoji=SYSTEM,
                    description="System usage",
                ),
                discord.SelectOption(
                    label="General Info",
                    emoji=ZYROX_GLOBAL,
                    description="General info",
                ),
                discord.SelectOption(
                    label="Team Info",
                    emoji=CODEBASE,
                    description="Bot team",
                ),
                discord.SelectOption(
                    label="Code Info",
                    emoji=ZYROX_SEARCH,
                    description="Code stats",
                ),
            ],
        )
        self.select.callback = self.on_select

        self.add_item(
            Container(
                TextDisplay(f"**{BRAND_NAME} Stats Panel**"),
                Separator(visible=True),
                TextDisplay(create_stats_content(stats_data, "Quick Overview")),
                ActionRow(self.select),
            )
        )

    async def on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "Only the command invoker can use this menu.", ephemeral=True
            )
            return

        selected_value = interaction.data.get("values", ["Quick Overview"])[0]

        new_container = Container(
            TextDisplay(f"**{BRAND_NAME} Stats Panel**"),
            Separator(visible=True),
            TextDisplay(create_stats_content(self.stats_data, selected_value)),
            ActionRow(self.select),
        )

        self.clear_items()
        self.add_item(new_container)

        await interaction.response.edit_message(view=self)


class StatsLoadingView(LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            Container(
                TextDisplay(
                    f"{LOADING} **Generating {BRAND_NAME} Statistics...**"
                )
            )
        )


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.total_songs_played = 0
        self.command_usage_count = 0
        self.bot.loop.create_task(self.setup_database())

    async def setup_database(self):
        async with aiosqlite.connect("db/stats.db") as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS stats (key TEXT PRIMARY KEY, value INTEGER)"
            )
            await db.commit()

            cursor = await db.execute(
                "SELECT value FROM stats WHERE key = 'total_songs_played'"
            )
            row = await cursor.fetchone()
            self.total_songs_played = row[0] if row else 0

            cursor = await db.execute(
                "SELECT value FROM stats WHERE key = 'command_usage_count'"
            )
            row = await cursor.fetchone()
            self.command_usage_count = row[0] if row else 0

    def format_number(self, num):
        if num < 1000:
            return str(num)
        elif num < 1_000_000:
            return f"{num / 1_000:.4f}k"
        elif num < 1_000_000_000:
            return f"{num / 1_000_000:.2f}M"
        else:
            return f"{num / 1_000_000_000:.2f}B"

    @commands.hybrid_command(
        name="stats",
        aliases=["botstats", "statistics", "botinfo"],
        help="Shows the bot's information.",
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def stats(self, ctx):
        loading_view = StatsLoadingView()
        loading_msg = await ctx.reply(view=loading_view)

        uptime = str(
            datetime.timedelta(seconds=int(round(time.time() - self.start_time)))
        )
        total_users = sum(g.member_count for g in self.bot.guilds if g.member_count)
        slash_cmds = len(self.bot.tree.get_commands())
        all_cmds = len(set(self.bot.walk_commands()))
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_usage = psutil.virtual_memory().percent

        stats_data = {
            "guilds": len(self.bot.guilds),
            "users": total_users,
            "uptime": uptime,
            "cpu": cpu_usage,
            "ram": ram_usage,
            "all_cmds": all_cmds,
            "slash_cmds": slash_cmds,
            "files": 0,
            "lines": 0,
            "words": 0,
        }

        files, lines, words = analyze_codebase(".")
        stats_data["files"] = files
        stats_data["lines"] = lines
        stats_data["words"] = words

        main_view = StatsView(ctx, stats_data)
        await loading_msg.edit(view=main_view)


async def setup(bot):
    await bot.add_cog(Stats(bot))

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

from discord.ext import commands, tasks
from discord import *
import discord
from utils.emoji import BOOST, ICONS_WARNING, INFO, MENTION, PREMIUM, TICK, TIME, TIMER_ALT1, U_ADMIN, ZDIL, ZHUMAN, ZYROXHAMMER, ZYROXSYS
import aiosqlite
from typing import Optional
from datetime import datetime, timedelta
from discord.ui import View, Button, Select
from utils.config import OWNER_IDS
from utils import Paginator, DescriptionEmbedPaginator
from utils.cv2 import CV2Embed, add_action_rows
from utils.config import *


def load_owner_ids():
    return OWNER_IDS


async def is_staff(user, staff_ids):
    return user.id in staff_ids


async def is_owner_or_staff(ctx):
    return await is_staff(ctx.author, ctx.cog.staff) or ctx.author.id in OWNER_IDS


class TimeSelect(Select):
    def __init__(self, user, db_path, author):
        super().__init__(placeholder="Select the duration")
        self.user = user
        self.db_path = db_path
        self.author = author

        self.options = [
            SelectOption(
                label="10 Minutes", description="Trial for 10 minutes", value="10m"
            ),
            SelectOption(
                label="1 Week", description="No prefix for 1 week", value="1w"
            ),
            SelectOption(
                label="3 Weeks", description="No prefix for 3 weeks", value="3w"
            ),
            SelectOption(
                label="1 Month", description="No prefix for 1 Month", value="1m"
            ),
            SelectOption(
                label="3 Months", description="No prefix for 3 Months.", value="3m"
            ),
            SelectOption(
                label="6 Months", description="No prefix for 6 Months.", value="6m"
            ),
            SelectOption(
                label="1 Year", description="No prefix for 1 Year.", value="1y"
            ),
            SelectOption(
                label="3 Years", description="No prefix for 3 Years.", value="3y"
            ),
            SelectOption(
                label="Lifetime", description="No prefix Permanently.", value="lifetime"
            ),
        ]

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message(
                "You can't select this option.", ephemeral=True
            )

        duration_mapping = {
            "10m": timedelta(minutes=10),
            "1w": timedelta(weeks=1),
            "3w": timedelta(weeks=3),
            "1m": timedelta(days=30),
            "3m": timedelta(days=90),
            "6m": timedelta(days=180),
            "1y": timedelta(days=365),
            "3y": timedelta(days=365 * 3),
            "lifetime": None,
        }

        selected_duration = self.values[0]
        expiry_time = None

        if selected_duration != "lifetime":
            expiry_time = datetime.utcnow() + duration_mapping[selected_duration]
            expiry_str = expiry_time.isoformat()
        else:
            expiry_str = None

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO np (id, expiry_time) VALUES (?, ?)",
                (self.user.id, expiry_str),
            )
            await db.commit()

        expiry_text = (
            "**Lifetime**"
            if selected_duration == "lifetime"
            else f"{expiry_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        expiry_timestamp = (
            "None (Permanent)"
            if selected_duration == "lifetime"
            else f"<t:{int(expiry_time.timestamp())}:f>"
        )

        guild = interaction.client.get_guild(1401125905677553716)
        if guild:
            member = guild.get_member(self.user.id)
            if member:
                role = guild.get_role(1401134167873290311)
                if role:
                    await member.add_roles(role, reason="No prefix added")

        log_channel = interaction.client.get_channel(LOG_CHANNEL_ID) if LOG_CHANNEL_ID else None
        if log_channel:
            embed = CV2Embed(
                title="User Added to No Prefix",
                description=f"**User**: [{self.user}](https://discord.com/users/{self.user.id})\n**User Mention**: {self.user.mention}\n** ID**: {self.user.id}\n\n** Added By**: [{self.author.display_name}](https://discord.com/users/{self.author.id})\n{TIMER_ALT1}**Expiry Time**: {expiry_text}\n{ZDIL} **Timestamp**: {expiry_timestamp}\n\n{PREMIUM} **Tier**: **{self.values[0].upper()}**",
                color=0xFF0000,
            )
            embed.set_thumbnail(
                url=self.user.avatar.url
                if self.user.avatar
                else self.user.default_avatar.url
            )
            await log_channel.send(view=embed)

        embed = CV2Embed(
            description=f"**Added Global No Prefix**:\n{ZHUMAN} User: **{self.user.mention}**\n{MENTION} User Mention: {self.user.mention}\n{ZYROXSYS} User ID: {self.user.id}\n\n__**Additional Info**__:\n{ZYROXHAMMER} Added By: **{self.author.display_name}**\n{TIME} Expiry Time: {expiry_text}\n{BOOST} Timestamp: {expiry_timestamp}",
            color=0xFF0000,
        )
        embed.set_author(
            name="Added No Prefix",
            icon_url="https://cdn.discordapp.com/icons/1166303696263585852/eeb00b2cf541438e88cdf842394c5b30.png?size=1024",
        )
        embed.set_footer(
            text="DM will be sent to the user in case No prefix is expired."
        )
        await interaction.response.edit_message(view=embed)


class TimeSelectView(View):
    def __init__(self, user, db_path, author):
        super().__init__()
        self.user = user
        self.db_path = db_path
        self.author = author
        self.add_item(TimeSelect(user, db_path, author))


from utils.config import BotName

class NoPrefix(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.staff = set()
        self.db_path = "db/np.db"
        self.client.loop.create_task(self.load_staff())
        self.client.loop.create_task(self.setup_database())
        self.expiry_check.start()

    async def setup_database(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS np (
                    id INTEGER PRIMARY KEY
                )
            """)

            async with db.execute("PRAGMA table_info(np);") as cursor:
                columns = [info[1] for info in await cursor.fetchall()]

            if "expiry_time" not in columns:
                await db.execute("""
                    ALTER TABLE np ADD COLUMN expiry_time TEXT NULL;
                """)

            await db.execute("""
                UPDATE np
                SET expiry_time = NULL
                WHERE expiry_time IS NULL;
            """)
            await db.execute("""
    CREATE TABLE IF NOT EXISTS autonp (
        guild_id INTEGER PRIMARY KEY
    )
    """)

            await db.commit()

    async def load_staff(self):
        await self.client.wait_until_ready()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id FROM staff") as cursor:
                self.staff = {row[0] for row in await cursor.fetchall()}

    @tasks.loop(minutes=10)
    async def expiry_check(self):
        async with aiosqlite.connect(self.db_path) as db:
            now = datetime.utcnow().isoformat()
            async with db.execute(
                "SELECT id FROM np WHERE expiry_time IS NOT NULL AND expiry_time <= ?",
                (now,),
            ) as cursor:
                expired_users = [row[0] for row in await cursor.fetchall()]

            if expired_users:
                async with db.execute(
                    "DELETE FROM np WHERE id IN ({})".format(
                        ",".join("?" * len(expired_users))
                    ),
                    expired_users,
                ):
                    await db.commit()

                for user_id in expired_users:
                    user = self.client.get_user(user_id)
                    if user:
                        log_channel = self.client.get_channel(LOG_CHANNEL_ID) if LOG_CHANNEL_ID else None
                        if log_channel:
                            embed_log = CV2Embed(
                                title="No Prefix Expired",
                                description=(
                    f"**User**: [{user}](https://discord.com/users/{user.id})\n"
                    f"**User Mention**: {user.mention}\n"
                    f"**ID**: {user.id}\n\n"
                    f"**Removed By**: **{BotName}**\n"
                ),
                                color=0xFF0000,
                            )
                            embed_log.set_thumbnail(
                                url=user.display_avatar.url
                                if user.avatar
                                else user.default_avatar.url
                            )
                            embed_log.set_footer(text="No Prefix Removal Log")
                            await log_channel.send(view=embed_log)
                        bot = self.client
                        guild = bot.get_guild(1401125905677553716)
                        if guild:
                            member = guild.get_member(user.id)
                            if member:
                                role = guild.get_role(1401134167873290311)
                                if role in member.roles:
                                    await member.remove_roles(role)

                        embed = CV2Embed(
                            description=f"{ICONS_WARNING} Your No Prefix status has **Expired**. You will now require the prefix to use commands.",
                            color=0xFF0000,
                        )
                        embed.set_author(
                            name="No Prefix Expired",
                            icon_url=user.avatar.url
                            if user.avatar
                            else user.default_avatar.url,
                        )

                        embed.set_footer(
                            text=f"{BRAND_NAME}  - No Prefix, Join support to regain access."
                        )
                        support = Button(
                            label="Support",
                            style=discord.ButtonStyle.link,
                            url=f"https://discord.gg/codexdev",
                        )
                        view = View()
                        view.add_item(support)

                        try:
                            add_action_rows(embed, view.children)
                            await user.send(f"{user.mention}", view=embed)
                        except discord.Forbidden:
                            pass
                        except discord.HTTPException:
                            pass

    @expiry_check.before_loop
    async def before_expiry_check(self):
        await self.client.wait_until_ready()

    @commands.group(
        name="np",
        help="Allows you to add someone to the no-prefix list (owner-only command)",
    )
    @commands.check(is_owner_or_staff)
    async def _np(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_np.command(name="list", help="List of no-prefix users")
    @commands.check(is_owner_or_staff)
    async def np_list(self, ctx):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id FROM np") as cursor:
                ids = [row[0] for row in await cursor.fetchall()]
                if not ids:
                    await ctx.reply(
                        f"No users in the no-prefix list.", mention_author=False
                    )
                    return
                entries = [
                    f"`#{no + 1}`  [Profile URL](https://discord.com/users/{mem}) (ID: {mem})"
                    for no, mem in enumerate(ids, start=0)
                ]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(
                        entries=entries,
                        title=f"No Prefix Users [{len(ids)}]",
                        description="",
                        per_page=10,
                        color=0xFF0000,
                    ),
                    ctx=ctx,
                )
                await paginator.paginate()

    @_np.command(name="add", help="Add user to no-prefix with time options")
    @commands.check(is_owner_or_staff)
    async def np_add(self, ctx, user: discord.User):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id FROM np WHERE id = ?", (user.id,)
            ) as cursor:
                result = await cursor.fetchone()
            if result:
                embed = CV2Embed(
                    description=f"**{user}** is Already in No prefix list\n\n **Requested By**: [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n",
                    color=0xFF0000,
                )
                embed.set_author(name="Error")
                await ctx.reply(view=embed)
                return

        view = TimeSelectView(user, self.db_path, ctx.author)
        from discord.ui import ActionRow

        embed = CV2Embed(
            title="Select No Prefix Duration",
            description="**Choose the duration for how long no-prefix should be enabled for this user:**",
            color=0xFF0000,
        )
        for item in view.children:
            embed.children[0].add_item(ActionRow(item))
        await ctx.reply(view=embed)

    @_np.command(name="remove", help="Remove user from no-prefix")
    @commands.check(is_owner_or_staff)
    async def np_remove(self, ctx, user: discord.User):
        async with aiosqlite.connect("db/np.db") as db:
            async with db.execute(
                "SELECT id FROM np WHERE id = ?", (user.id,)
            ) as cursor:
                result = await cursor.fetchone()
            if not result:
                embed = CV2Embed(
                    description=f"**{user}** is Not in the No Prefix list\n\n{U_ADMIN} **Requested By**: [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n",
                    color=0xFF0000,
                )
                embed.set_author(name="Error")
                await ctx.reply(view=embed)
                return

            await db.execute("DELETE FROM np WHERE id = ?", (user.id,))
            await db.commit()

        guild = ctx.bot.get_guild(1401125905677553716)
        if guild:
            member = guild.get_member(user.id)
            if member:
                role = guild.get_role(1401134167873290311)
                if role in member.roles:
                    await member.remove_roles(role)

        embed = CV2Embed(
            description=(
                f"**User**: [{user}](https://discord.com/users/{user.id})\n"
                f"**User Mention**: {user.mention}\n"
                f"** ID**: {user.id}\n\n"
                f"** Removed By**: **{BotName}**\n"
            ),
            color=0xFF0000,
        )
        embed.set_author(name="Removed No Prefix")
        await ctx.reply(view=embed)

        log_channel = ctx.bot.get_channel(LOG_CHANNEL_ID) if LOG_CHANNEL_ID else None
        if log_channel:
            embed_log = CV2Embed(
                title="No Prefix Removed",
                description=(
                    f"**User**: [{user}](https://discord.com/users/{user.id})\n"
                    f"**User Mention**: {user.mention}\n"
                    f"** ID**: {user.id}\n\n"
                    f"**Removed By**: **{BotName}**\n"
                ),
                color=0xFF0000,
            )
            embed_log.set_thumbnail(
                url=user.display_avatar.url if user.avatar else user.default_avatar.url
            )
            embed_log.set_footer(text="No Prefix Removal Log")
            await log_channel.send(" ".join(f"<@{oid}>" for oid in OWNER_IDS), view=embed_log)

    @_np.command(
        name="status", help="Check if a user is in the No Prefix list and show details."
    )
    @commands.check(is_owner_or_staff)
    async def np_status(self, ctx, user: discord.User):
        async with aiosqlite.connect("db/np.db") as db:
            async with db.execute(
                "SELECT id, expiry_time FROM np WHERE id = ?", (user.id,)
            ) as cursor:
                result = await cursor.fetchone()

            if not result:
                embed = CV2Embed(
                    title="No Prefix Status",
                    description=f"**{user}** is Not in the No Prefix list\n\n"
                    f"**Requested By**: "
                    f"[{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n",
                    color=0xFF0000,
                )
                await ctx.reply(view=embed)
                return

            user_id, expires = result

            if expires and expires != "Null":
                expire_time = datetime.fromisoformat(expires)
                expire_timestamp = f"<t:{int(expire_time.timestamp())}:F>"
            else:
                expire_time = "Lifetime"
                expire_timestamp = "Lifetime"

            embed = CV2Embed(
                title="No Prefix Status",
                description=(
                    f"**User**: [{user}](https://discord.com/users/{user.id})\n"
                    f"**User ID**: {user.id}\n\n"
                    f"{TIME} Expiry: {expire_time} ({expire_timestamp})"
                ),
                color=0xFF0000,
            )

            embed.set_thumbnail(
                url=user.display_avatar.url if user.avatar else user.default_avatar.url
            )

        await ctx.reply(view=embed)

    @commands.group(name="autonp", help="Manage auto no-prefix for partner guilds.")
    @commands.is_owner()
    async def autonp(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @autonp.group(name="guild", help="Manage partner guilds for auto no-prefix.")
    async def autonp_guild(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @autonp_guild.command(name="add", help="Add a guild to auto no-prefix.")
    async def add_guild(self, ctx, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM autonp WHERE guild_id = ?", (guild_id,)
            ) as cursor:
                if await cursor.fetchone():
                    await ctx.reply("Guild is already added.")
                    return
            await db.execute("INSERT INTO autonp (guild_id) VALUES (?)", (guild_id,))
            await db.commit()
        await ctx.reply(f"Guild {guild_id} added to auto no-prefix.")

    @autonp_guild.command(name="remove", help="Remove a guild from auto no-prefix.")
    async def remove_guild(self, ctx, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM autonp WHERE guild_id = ?", (guild_id,)
            ) as cursor:
                if not await cursor.fetchone():
                    await ctx.reply("Guild is not in auto no-prefix.")
                    return
            await db.execute("DELETE FROM autonp WHERE guild_id = ?", (guild_id,))
            await db.commit()
        await ctx.reply(f"Guild {guild_id} removed from auto no-prefix.")

    @autonp_guild.command(name="list", help="List all guilds with auto no-prefix.")
    @commands.check(is_owner_or_staff)
    async def list_guilds(self, ctx):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT guild_id FROM autonp") as cursor:
                guilds = [row[0] for row in await cursor.fetchall()]
                if not guilds:
                    await ctx.reply(
                        "No guilds in auto no-prefix.", mention_author=False
                    )
                    return
                await ctx.reply(
                    f"Guilds in auto no-prefix:\n" + "\n".join(str(g) for g in guilds),
                    mention_author=False,
                )

    async def is_user_in_np(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM np WHERE id = ?", (user_id,)
            ) as cursor:
                return await cursor.fetchone() is not None

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.premium_since is None and after.premium_since is not None:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT 1 FROM autonp WHERE guild_id = ?", (after.guild.id,)
                ) as cursor:
                    if not await cursor.fetchone():
                        return
            if not await self.is_user_in_np(after.id):
                await self.add_np(after, timedelta(days=60))
                log_channel = self.client.get_channel(1406566123234787378)
                embed = CV2Embed(
                    title="Added No prefix due to Boosting Partner Server",
                    description=f"**User**: **[{after}](https://discord.com/users/{after.id})** (ID: {after.id})\n**Server**: {after.guild.name}",
                    color=0xFF0000,
                )
                message = await log_channel.send(" ".join(f"<@{oid}>" for oid in OWNER_IDS), view=embed)
                await message.publish()

        elif before.premium_since is not None and after.premium_since is None:
            await self.handle_boost_removal(after)

    # @commands.Cog.listener()
    # async def on_member_remove(self, member):
    # await self.handle_boost_removal(member)

    async def handle_boost_removal(self, user):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM autonp WHERE guild_id = ?", (user.guild.id,)
            ) as cursor:
                if not await cursor.fetchone():
                    return
        if await self.is_user_in_np(user.id):
            await self.remove_np(user)
            log_channel = self.client.get_channel(1406566257070964756)
            embed = CV2Embed(
                title="Removed No prefix due to Unboosting Partner Server",
                description=f"**User**: **[{user}](https://discord.com/users/{user.id})** (ID: {user.id})\n**Server**: {user.guild.name}",
                color=0xFF0000,
            )
            message = await log_channel.send(" ".join(f"<@{oid}>" for oid in OWNER_IDS), view=embed)
            await message.publish()

    async def add_np(self, user, duration):
        expiry_time = datetime.utcnow() + duration
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO np (id, expiry_time) VALUES (?, ?)",
                (user.id, expiry_time.isoformat()),
            )
            await db.commit()

        embed = CV2Embed(
            title="Congratulations you got 2 months No Prefix!",
            description=f"You've been credited 2 months of global No Prefix for boosting our Partnered Servers. You can now use my commands without prefix. If you wish to remove it, please reach out [Support Server](https://discord.gg/codexdev).",
            color=0xFF0000,
        )
        try:
            await user.send(view=embed)
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

        guild = self.client.get_guild(1401125905677553716)
        if guild:
            member = guild.get_member(user.id)
            if member is not None:
                role = guild.get_role(1401134167873290311)
                if role:
                    await member.add_roles(role)

    async def remove_np(self, user):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT expiry_time FROM np WHERE id = ?", (user.id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row is None or row[0] is None:
                    return

            await db.execute("DELETE FROM np WHERE id = ?", (user.id,))
            await db.commit()

        embed = CV2Embed(
            title=f"{ICONS_WARNING} Global No Prefix Expired",
            description=f"Hey {user.mention}, your global no prefix has expired!\n\n__**Reason:**__ Unboosting our partnered Server.\nIf you think this is a mistake then please reach out [Support Server](https://discord.gg/codexdev).",
            color=0xFF0000,
        )

        try:
            await user.send(view=embed)
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

        guild = self.client.get_guild(1401125905677553716)
        if guild:
            member = guild.get_member(user.id)
            if member is not None:
                role = guild.get_role(1401134167873290311)
                if role and role in member.roles:
                    await member.remove_roles(role)

    @_np.command(name="reset", help="Reset/clear all users from the no-prefix list")
    @commands.is_owner()
    async def np_reset(self, ctx):
        # Confirmation message
        embed = CV2Embed(
            title="Confirm Reset",
            description="Are you sure you want to remove **ALL** users from the no-prefix list? This action cannot be undone.",
            color=0xFF0000,
        )

        # Create confirmation buttons
        yes_button = Button(label="Yes", style=discord.ButtonStyle.danger)
        no_button = Button(label="No", style=discord.ButtonStyle.secondary)

        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        # Define button callbacks
        async def yes_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message(
                    "This interaction is not for you.", ephemeral=True
                )

            # Remove all users from no-prefix list
            async with aiosqlite.connect(self.db_path) as db:
                # Get count of users before deletion
                async with db.execute("SELECT COUNT(*) FROM np") as cursor:
                    count = (await cursor.fetchone())[0]

                # Delete all entries
                await db.execute("DELETE FROM np")
                await db.commit()

            # Remove roles from all members in the main guild
            guild = self.client.get_guild(1401125905677553716)
            if guild:
                role = guild.get_role(1401134167873290311)
                if role:
                    members_with_role = [
                        member for member in guild.members if role in member.roles
                    ]
                    for member in members_with_role:
                        try:
                            await member.remove_roles(
                                role, reason="Global no-prefix reset"
                            )
                        except discord.HTTPException:
                            pass

            # Send success message
            success_embed = CV2Embed(
                title=f"{TICK} No-Prefix Reset Complete",
                description=f"Successfully removed {count} users from the no-prefix list.",
                color=0xFF0000,
            )
            await interaction.response.edit_message(view=success_embed)

            # Log the action
            log_channel = self.client.get_channel(LOG_CHANNEL_ID) if LOG_CHANNEL_ID else None
            if log_channel:
                log_embed = CV2Embed(
                    title="No-Prefix List Reset",
                    description=f"**Reset By**: [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n{INFO} Users Removed: {count}",
                    color=0xFF0000,
                )
                log_embed.set_footer(text="No Prefix Reset Log")
                await log_channel.send(view=log_embed)

        async def no_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message(
                    "This interaction is not for you.", ephemeral=True
                )

            cancel_embed = CV2Embed(
                title="Reset Cancelled",
                description="No changes have been made to the no-prefix list.",
                color=0xFF0000,
            )
            await interaction.response.edit_message(view=cancel_embed)

        yes_button.callback = yes_callback
        no_button.callback = no_callback

        add_action_rows(embed, view.children)
        await ctx.reply(view=embed)

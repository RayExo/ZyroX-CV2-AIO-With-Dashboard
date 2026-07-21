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
from discord.ext import commands
from discord import *
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import discord
import json
import datetime
import asyncio
import aiosqlite
from typing import Optional
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
from utils.Tools import *
from utils.config import OWNER_IDS, BOT_OWNER_IDS
from utils.emoji import BOOSTS, DISCORD_BADGE_EMOJIS, LOADINGRED, NITRO_BOOST, TICK, ZWARNING
from core import Cog, zyrox, Context
import sqlite3
import os
import requests
import numpy as np
from io import BytesIO
from utils.config import OWNER_IDS, BOT_OWNER_IDS
from discord.errors import Forbidden
from discord import Embed
from discord.ui import Button, View
from utils.config import *

# p1


# --- Configuration & Helpers ---
# OWNER_IDS and BOT_OWNER_IDS are imported from utils.config — edit .env to change them

# Your custom bot badges, including Family and Developer
BADGE_URLS = {
    "owner": "https://cdn.discordapp.com/emojis/1448951721479901334.png?v=1&size=48&quality=lossless",
    "staff": "https://cdn.discordapp.com/emojis/1448949616681812098.png?v=1&size=48&quality=lossless",
    "partner": "https://cdn.discordapp.com/emojis/1448949605676093540.png?v=1&size=48&quality=lossless",
    "sponsor": "https://cdn.discordapp.com/emojis/1448949571811282984.png?v=1&size=48&quality=lossless",
    "friend": "https://cdn.discordapp.com/emojis/1448951509235531869.png?v=1&size=48&quality=lossless",
    "early": "https://cdn.discordapp.com/emojis/1448949582573867039.png?v=1&size=48&quality=lossless",
    "vip": "https://cdn.discordapp.com/emojis/1448951307707748395.png?v=1&size=48&quality=lossless",
    "bug": "https://cdn.discordapp.com/emojis/1448949593923518485.png?v=1&size=48&quality=lossless",
    "developer": "https://cdn.discordapp.com/emojis/1448951697853386826.png?v=1&size=48&quality=lossless",
    "family": "https://cdn.discordapp.com/emojis/1448951456861519962.png?v=1&size=48&quality=lossless", # New Family Badge
}

BADGE_NAMES = {
    "owner": "Owner", "staff": "Staff", "partner": "Partner",
    "sponsor": "Sponsor", "friend": "Friends", "early": "Early Supporter",
    "vip": "VIP", "bug": "Bug Hunter", "developer": "Developer", "family": "Family"
}

# Emojis for official Discord badges (imported from utils.emoji)
# Keep reference for backward compatibility
BACK_COMPAT_BADGE_DICT = DISCORD_BADGE_EMOJIS


db_folder = 'db'
db_file = 'badges.db'
db_path = os.path.join(db_folder, db_file)
FONT_PATH = os.path.join('utils', 'arial.ttf') 

# --- Database Setup ---
os.makedirs(db_folder, exist_ok=True)
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS badges (user_id INTEGER PRIMARY KEY)')
conn.commit()

for badge_name in BADGE_NAMES:
    try:
        c.execute(f"ALTER TABLE badges ADD COLUMN {badge_name} INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass

# --- Helper Functions ---
def add_badge(user_id, badge):
    try:
        if badge not in BADGE_URLS: return False
        c.execute("SELECT 1 FROM badges WHERE user_id = ?", (user_id,))
        if c.fetchone() is None:
            c.execute(f"INSERT INTO badges (user_id, {badge}) VALUES (?, 1)", (user_id,))
        else:
            c.execute(f"UPDATE badges SET {badge} = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    except sqlite3.Error:
        return False

def remove_badge(user_id, badge):
    try:
        if badge not in BADGE_URLS: return False
        c.execute(f"UPDATE badges SET {badge} = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    except sqlite3.Error:
        return False

async def is_owner_or_staff(ctx):
    owner_cog = ctx.bot.get_cog("Owner")
    is_staff_member = False
    if owner_cog:
        is_staff_member = ctx.author.id in getattr(owner_cog, 'staff', set())
    return is_staff_member or ctx.author.id in OWNER_IDS

def blacklist_check():
    async def predicate(ctx): return True
    return commands.check(predicate)

def ignore_check():
    async def predicate(ctx): return True
    return commands.check(predicate)


from utils.config import BotName

class Owner(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.staff = set()
        self.np_cache = []
        self.db_path = 'db/np.db'
        self.stop_tour = False
        self.bot_owner_ids = BOT_OWNER_IDS
        self.client.loop.create_task(self.setup_database())
        self.client.loop.create_task(self.load_staff())
        

    async def setup_database(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS staff (
                    id INTEGER PRIMARY KEY
                )
            ''')
            await db.commit()

    

    async def load_staff(self):
        await self.client.wait_until_ready()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT id FROM staff') as cursor:
                self.staff = {row[0] for row in await cursor.fetchall()}

    @commands.command(name="staff_add", aliases=["staffadd", "addstaff"], help="Adds a user to the staff list.")
    @commands.is_owner()
    async def staff_add(self, ctx, user: discord.User):
        if user.id in self.staff:
            sonu = discord.Embed(title=f"{ZWARNING}  Access Denied", description=f"{user} is already in the staff list.", color=0xFF0000)
            await ctx.reply(embed=sonu, mention_author=False)
        else:
            self.staff.add(user.id)
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('INSERT OR IGNORE INTO staff (id) VALUES (?)', (user.id,))
                await db.commit()
            sonu2 = discord.Embed(title=f"{TICK} Success", description=f"Added {user} to the staff list.", color=0xFF0000)
            await ctx.reply(embed=sonu2, mention_author=False)

    @commands.command(name="staff_remove", aliases=["staffremove", "removestaff"], help="Removes a user from the staff list.")
    @commands.is_owner()
    async def staff_remove(self, ctx, user: discord.User):
        if user.id not in self.staff:
            sonu = discord.Embed(title=f"{ZWARNING} Access Denied", description=f"{user} is not in the staff list.", color=0xFF0000)
            await ctx.reply(embed=sonu, mention_author=False)
        else:
            self.staff.remove(user.id)
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('DELETE FROM staff WHERE id = ?', (user.id,))
                await db.commit()
                sonu2 = discord.Embed(title=f"{TICK} Success", description=f"Removed {user} from the staff list.", color=0xFF0000)
            await ctx.reply(embed=sonu2, mention_author=False)

    @commands.command(name="staff_list", aliases=["stafflist", "liststaff", "staffs"], help="Lists all staff members.")
    @commands.is_owner()
    async def staff_list(self, ctx):
        if not self.staff:
            await ctx.send("The staff list is currently empty.")
        else:
            member_list = []
            for staff_id in self.staff:
                member = await self.client.fetch_user(staff_id)
                member_list.append(f"{member.name}#{member.discriminator} (ID: {staff_id})")
            staff_display = "\n".join(member_list)
            sonu = discord.Embed(title=f"{TICK} {BotName} Staffs", description=f"\n{staff_display}", color=0xFF0000)
            await ctx.send(embed=sonu)

    @commands.command(name="slist")
    @commands.check(is_owner_or_staff)
    async def _slist(self, ctx):
        servers = sorted(self.client.guilds, key=lambda g: g.member_count, reverse=True)
        entries = [
            f"`#{i}` | [{g.name}](https://discord.com/guilds/{g.id}) - {g.member_count}"
            for i, g in enumerate(servers, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            description="",
            title=f"Guild List of {BotName} [{len(self.client.guilds)}]",
            color=0xFF0000,
            per_page=10),
            ctx=ctx)
        await paginator.paginate()


    @commands.command(name="mutuals", aliases=["mutual"])
    @commands.is_owner()
    async def mutuals(self, ctx, user: discord.User):
        guilds = [guild for guild in self.client.guilds if user in guild.members]
        entries = [
            f"`#{no}` | [{guild.name}](https://discord.com/channels/{guild.id}) - {guild.member_count}"
            for no, guild in enumerate(guilds, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            description="",
            title=f"Mutual Guilds of {user.name} [{len(guilds)}]",
            color=0xFF0000,
            per_page=10),
            ctx=ctx)
        await paginator.paginate()

    @commands.command(name="getinvite", aliases=["gi", "guildinvite"])
    @commands.is_owner()
    async def getinvite(self, ctx: Context, guild= discord.Guild):   
        if not guild:
            await ctx.send("Invalid server.")
            return

        perms_ha = guild.me.guild_permissions.view_audit_log
        invite_krskta = guild.me.guild_permissions.create_instant_invite

        try:
            invites = await guild.invites()
            if invites:
                entries = [f"{invite.url} - {invite.uses} uses" for invite in invites]
                paginator = Paginator(source=DescriptionEmbedPaginator(
                    entries=entries,
                    title=f"Active Invites for {guild.name}",
                    description="",
                    per_page=10,
                    color=0xFF0000),
                    ctx=ctx)
                await paginator.paginate()
            elif invite_krskta:
                channel = guild.system_channel or next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).create_instant_invite), None)
                if channel:
                    invite = await channel.create_invite(max_age=86400, max_uses=1, reason="No active invites found, creating a new one.")
                    await ctx.send(f"Created new invite: {invite.url}")
                else:
                    await ctx.send("No channel found.")
            else:
                await ctx.send("Can't create invites.")
        except discord.Forbidden:
            await ctx.send("Forbidden.")


    @commands.command(name="reload", help="Restarts the client.")
    @commands.is_owner()
    async def _restart(self, ctx: Context):
        await ctx.reply(f"{TICK} | **Successfully Restarting {BotName} It Takes 10 seconds**")
        restart_program()

    @commands.command(name="sync", help="Syncs all database.")
    @commands.is_owner()
    async def _sync(self, ctx):
        await ctx.reply("Syncing...", mention_author=False)
        with open('events.json', 'r') as f:
            data = json.load(f)
        for guild in self.client.guilds:
            if str(guild.id) not in data['guild']:
                data['guilds'][str(guild.id)] = 'on'
                with open('events.json', 'w') as f:
                    json.dump(data, f, indent=4)
            else:
                pass
        with open('config.json', 'r') as f:
            data = json.load(f)
        for op in data["guilds"]:
            g = self.client.get_guild(int(op))
            if not g:
                data["guilds"].pop(str(op))
                with open('config.json', 'w') as f:
                    json.dump(data, f, indent=4)


    @commands.command(name="owners")
    @commands.is_owner()
    async def own_list(self, ctx):
        nplist = OWNER_IDS
        npl = ([await self.client.fetch_user(nplu) for nplu in nplist])
        npl = sorted(npl, key=lambda nop: nop.created_at)
        entries = [
            f"`#{no}` | [{mem}](https://discord.com/users/{mem.id}) (ID: {mem.id})"
            for no, mem in enumerate(npl, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            title=f"{BRAND_NAME} Owners [{len(nplist)}]",
            description="",
            per_page=10,
            color=0xFF0000),
                              ctx=ctx)
        await paginator.paginate()





    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx, user: discord.User, *, message: str):
        """ DM the user of your choice """
        try:
            await user.send(message)
            await ctx.send(f"{TICK} | Successfully Sent a DM to **{user}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")           



    @commands.group()
    @commands.is_owner()
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))


    @change.command(name="nickname")
    @commands.is_owner()
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"{TICK} | Successfully changed nickname to **{name}**")
            else:
                await ctx.send(f"{TICK} | Successfully removed nickname")
        except Exception as err:
            await ctx.send(err) 


    @commands.command(name="ownerban", aliases=["forceban", "dna"])
    @commands.is_owner()
    async def _ownerban(self, ctx: Context, user_id: int, *, reason: str = "No reason provided"):
        
        member = ctx.guild.get_member(user_id)
        if member:
            try:
                await member.ban(reason=reason)
                embed = discord.Embed(
                    title="Successfully Banned",
                    description=f"{TICK} | **{member.name}** has been successfully banned from {ctx.guild.name} by the Bot Owner.",
                    color=0xFF0000)
                await ctx.reply(embed=embed, mention_author=False, delete_after=3)
                await ctx.message.delete()
            except discord.Forbidden:
                embed = discord.Embed(
                    title="Error!",
                    description=f"{ZWARNING}  I do not have permission to ban **{member.name}** in this guild.",
                    color=0xFF0000
                )
                await ctx.reply(embed=embed, mention_author=False, delete_after=5)
                await ctx.message.delete()
            except discord.HTTPException:
                embed = discord.Embed(
                    title="Error!",
                    description=f"{ZWARNING}  An error occurred while banning **{member.name}**.",
                    color=0xFF0000
                )
                await ctx.reply(embed=embed, mention_author=False, delete_after=5)
                await ctx.message.delete()
        else:
            await ctx.reply("User not found in this guild.", mention_author=False, delete_after=3)
            await ctx.message.delete()

    @commands.command(name="ownerunban", aliases=["forceunban"])
    @commands.is_owner()
    async def _ownerunban(self, ctx: Context, user_id: int, *, reason: str = "No reason provided"):
        user = self.client.get_user(user_id)
        if user:
            try:
                await ctx.guild.unban(user, reason=reason)
                embed = discord.Embed(
                    title="Successfully Unbanned",
                    description=f"{TICK} | **{user.name}** has been successfully unbanned from {ctx.guild.name} by the Bot Owner.",
                    color=0xFF0000
                )
                await ctx.reply(embed=embed, mention_author=False)
            except discord.Forbidden:
                embed = discord.Embed(
                    title="Error!",
                    description=f"{ZWARNING}  I do not have permission to unban **{user.name}** in this guild.",
                    color=0xFF0000
                )
                await ctx.reply(embed=embed, mention_author=False)
            except discord.HTTPException:
                embed = discord.Embed(
                    title="Error!",
                    description=f"{ZWARNING}  An error occurred while unbanning **{user.name}**.",
                    color=0xFF0000
                )
                await ctx.reply(embed=embed, mention_author=False)
        else:
            await ctx.reply("User not found.", mention_author=False)



    @commands.command(name="globalunban")
    @commands.is_owner()
    async def globalunban(self, ctx: Context, user: discord.User):
        success_guilds = []
        error_guilds = []

        for guild in self.client.guilds:
            bans = await guild.bans()
            if any(ban_entry.user.id == user.id for ban_entry in bans):
                try:
                    await guild.unban(user, reason="Global Unban")
                    success_guilds.append(guild.name)
                except discord.HTTPException:
                    error_guilds.append(guild.name)
                except discord.Forbidden:
                    error_guilds.append(guild.name)

        user_mention = f"{user.mention} (**{user.name}**)"

        success_message = f"Successfully unbanned {user_mention} from the following guild(s):\n{',     '.join(success_guilds)}" if success_guilds else "No guilds where the user was successfully unbanned."
        error_message = f"Failed to unban {user_mention} from the following guild(s):\n{',    '.join(error_guilds)}" if error_guilds else "No errors during unbanning."

        await ctx.reply(f"{success_message}\n{error_message}", mention_author=False)

    @commands.command(name="guildban")
    @commands.is_owner()
    async def guildban(self, ctx: Context, guild_id: int, user_id: int, *, reason: str = "No reason provided"):
        guild = self.client.get_guild(guild_id)
        if not guild:
            await ctx.reply("Bot is not present in the specified guild.", mention_author=False)
            return

        member = guild.get_member(user_id)
        if member:
            try:
                await guild.ban(member, reason=reason)
                await ctx.reply(f"Successfully banned **{member.name}** from {guild.name}.", mention_author=False)
            except discord.Forbidden:
                await ctx.reply(f"Missing permissions to ban **{member.name}** in {guild.name}.", mention_author=False)
            except discord.HTTPException as e:
                await ctx.reply(f"An error occurred while banning **{member.name}** in {guild.name}: {str(e)}", mention_author=False)
        else:
            await ctx.reply(f"User not found in the specified guild {guild.name}.", mention_author=False)

    @commands.command(name="guildunban")
    @commands.is_owner()
    async def guildunban(self, ctx: Context, guild_id: int, user_id: int, *, reason: str = "No reason provided"):
        guild = self.client.get_guild(guild_id)
        if not guild:
            await ctx.reply("Bot is not present in the specified guild.", mention_author=False)
            return
        #member = guild.get_member(user_id)

        try:
            user = await self.client.fetch_user(user_id)
        except discord.NotFound:
            await ctx.reply(f"User with ID {user_id} not found.", mention_author=False)
            return

        user = discord.Object(id=user_id)
        try:
            await guild.unban(user, reason=reason)
            await ctx.reply(f"Successfully unbanned user ID {user_id} from {guild.name}.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply(f"Missing permissions to unban user ID {user_id} in {guild.name}.", mention_author=False)
        except discord.HTTPException as e:
            await ctx.reply(f"An error occurred while unbanning user ID {user_id} in {guild.name}: {str(e)}", mention_author=False)


    @commands.command(name="leaveguild", aliases=["leavesv"])
    @commands.is_owner()
    async def leave_guild(self, ctx, guild_id: int):
        guild = self.client.get_guild(guild_id)
        if guild is None:
            await ctx.send(f"Guild with ID {guild_id} not found.")
            return

        await guild.leave()
        await ctx.send(f"Left the guild: {guild.name} ({guild.id})")

    @commands.command(name="guildinfo")
    @commands.check(is_owner_or_staff)
    async def guild_info(self, ctx, guild_id: int):
        guild = self.client.get_guild(guild_id)
        if guild is None:
            await ctx.send(f"Guild with ID {guild_id} not found.")
            return

        embed = discord.Embed(
            title=guild.name,
            description=f"Information for guild ID {guild.id}",
            color=0x00000
        )
        embed.add_field(name="Owner", value=str(guild.owner), inline=True)
        embed.add_field(name="Member Count", value=str(guild.member_count), inline=True)
        embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        if guild.icon is not None:
                embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=f"Created at: {guild.created_at}")

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def servertour(self, ctx, time_in_seconds: int, member: discord.Member):
        guild = ctx.guild

        if time_in_seconds > 3600:
            await ctx.send("Time cannot be greater than 3600 seconds (1 hour).")
            return

        if not member.voice:
            await ctx.send(f"{member.display_name} is not in a voice channel.")
            return

        voice_channels = [ch for ch in guild.voice_channels if ch.permissions_for(guild.me).move_members]

        if len(voice_channels) < 2:
            await ctx.send("Not enough voice channels to move the user.")
            return

        self.stop_tour = False

        class StopButton(discord.ui.View):
            def __init__(self, outer_self):
                super().__init__(timeout=time_in_seconds)
                self.outer_self = outer_self

            @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
            async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id not in self.outer_self.bot_owner_ids:
                    await interaction.response.send_message("Only the bot owner can stop this process.", ephemeral=True)
                    return
                self.outer_self.stop_tour = True
                await interaction.response.send_message("Server tour has been stopped.", ephemeral=True)
                self.stop()

        view = StopButton(self)
        message = await ctx.send(f"Started moving {member.display_name} for {time_in_seconds} seconds. Click the button to stop.", view=view)

        end_time = asyncio.get_event_loop().time() + time_in_seconds

        while asyncio.get_event_loop().time() < end_time and not self.stop_tour:
            for ch in voice_channels:
                if self.stop_tour:
                    await ctx.send("Tour stopped.")
                    return
                if not member.voice:
                    await ctx.send(f"{member.display_name} left the voice channel.")
                    return
                try:
                    await member.move_to(ch)
                    await asyncio.sleep(5)
                except Forbidden:
                    await ctx.send(f"Missing permissions to move {member.display_name}.")
                    return
                except Exception as e:
                    await ctx.send(f"Error: {str(e)}")
                    return

        if not self.stop_tour:
            await message.edit(content=f"Finished moving {member.display_name} after {time_in_seconds} seconds.", view=None)




    


    @commands.group()
    @commands.check(is_owner_or_staff)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bdg(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description='Invalid `bdg` command passed. Use `add` or `remove`.', color=0xFF0000)
            await ctx.send(embed=embed)

    @bdg.command()
    @commands.check(is_owner_or_staff)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def add(self, ctx, member: discord.Member, badge: str):
        badge = badge.lower()
        user_id = member.id
        if badge in BADGE_URLS or badge == 'bug' or badge == 'all':
            if badge == 'all':
                for b in BADGE_URLS.keys():
                    add_badge(user_id, b)
                add_badge(user_id, 'bug')
                embed = discord.Embed(description=f"All badges added to {member.mention}.", color=0xFF0000)
                await ctx.send(embed=embed)
            else:
                success = add_badge(user_id, badge)
                if success:
                    embed = discord.Embed(description=f"Badge `{badge}` added to {member.mention}.", color=0xFF0000)
                else:
                    embed = discord.Embed(description=f"{member.mention} already has the badge `{badge}`.", color=0xFF0000)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"Invalid badge: `{badge}`", color=0xFF0000)
            await ctx.send(embed=embed)

    @bdg.command()
    @commands.check(is_owner_or_staff)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def remove(self, ctx, member: discord.Member, badge: str):
        badge = badge.lower()
        user_id = member.id
        if badge in BADGE_URLS or badge == 'bug' or badge == 'all':
            if badge == 'all':
                for b in BADGE_URLS.keys():
                    remove_badge(user_id, b)
                remove_badge(user_id, 'bug')
                embed = discord.Embed(description=f"All badges removed from {member.mention}.", color=0xFF0000)
                await ctx.send(embed=embed)
            else:
                success = remove_badge(user_id, badge)
                if success:
                    embed = discord.Embed(description=f"Badge `{badge}` removed from {member.mention}.", color=0xFF0000)
                else:
                    embed = discord.Embed(description=f"{member.mention} does not have the badge `{badge}`.", color=0xFF0000)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"Invalid badge: `{badge}`", color=0xFF0000)
            await ctx.send(embed=embed)


    @commands.command(name="forcepurgebots",
        aliases=["fpb"],
        help="Clear recently bot messages in channel (Bot owner only)")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.is_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def _purgebot(self, ctx, prefix=None, search=100):
        
        await ctx.message.delete()
        
        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))
        
        await do_removal(ctx, search, predicate)


    @commands.command(name="forcepurgeuser",
        aliases=["fpu"],
        help="Clear recent messages of a user in channel (Bot owner only)")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.is_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def purguser(self, ctx, member: discord.Member, search=100):
        
        await ctx.message.delete()
        
        await do_removal(ctx, search, lambda e: e.author == member)

        
# p2
class Badges(commands.Cog):
    """Handles the profile and badge display system."""
    def __init__(self, bot):
        self.bot = bot

    def generate_profile_image(self, member: discord.Member, user_bot_badges: dict):
        # --- Fonts and Colors ---
        font_title = ImageFont.truetype(FONT_PATH, 22)
        font_text = ImageFont.truetype(FONT_PATH, 18)
        font_badge = ImageFont.truetype(FONT_PATH, 20)
        
        BG_COLOR = (30, 31, 34)
        BOX_COLOR = (43, 45, 49)
        TEXT_COLOR = (255, 255, 255)
        
        W, H = (850, 450)
        img = Image.new('RGB', (W, H), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # --- Left Column (Avatar & Username) ---
        draw.text((40, 30), "Avatar:", font=font_title, fill=TEXT_COLOR)
        try:
            pfp_resp = requests.get(member.display_avatar.with_size(128).url)
            pfp_resp.raise_for_status()
            pfp = Image.open(BytesIO(pfp_resp.content)).convert("RGBA")
        except requests.RequestException:
            pfp = Image.new("RGBA", (128, 128), (0,0,0,0))
        pfp = pfp.resize((128, 128), Image.Resampling.LANCZOS)
        draw.rectangle((40, 70, 188, 218), fill=BOX_COLOR)
        img.paste(pfp, (50, 80), pfp)

        draw.text((40, 250), "Username:", font=font_title, fill=TEXT_COLOR)
        draw.rectangle((40, 290, 280, 340), fill=BOX_COLOR)
        draw.text((50, 300), str(member), font=font_text, fill=TEXT_COLOR)

        # --- Right Column (Bot Badges) ---
        draw.text((320, 30), "Badges:", font=font_title, fill=TEXT_COLOR)
        
        badge_priority = [
            "owner", "developer", "staff", "partner", "sponsor", 
            "vip", "friend", "early", "bug", "family"
        ]
        
        active_badges = [name for name in badge_priority if user_bot_badges.get(name) == 1]
        
        col_width, row_height, gap_x, gap_y = 220, 50, 20, 15
        start_x, start_y = 320, 70

        # Loop 10 times to draw all slots
        for i in range(10):
            col = i % 2
            row = i // 2
            
            x = start_x + col * (col_width + gap_x)
            y = start_y + row * (row_height + gap_y)
            
            # Always draw the empty block
            draw.rectangle((x, y, x + col_width, y + row_height), fill=BOX_COLOR)

            # If there's an active badge for this slot, draw it
            if i < len(active_badges):
                name = active_badges[i]
                try:
                    badge_resp = requests.get(BADGE_URLS[name])
                    badge_resp.raise_for_status()
                    icon = Image.open(BytesIO(badge_resp.content)).resize((30, 30))
                    img.paste(icon, (x + 10, y + 10), icon)
                except requests.RequestException:
                    pass
                draw.text((x + 50, y + 12), BADGE_NAMES[name], font=font_badge, fill=TEXT_COLOR)

        with BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            return discord.File(fp=image_binary, filename='profile.png')

    @commands.hybrid_command(name='profile', aliases=['pr', 'badgesf'])
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        
        loading_embed = discord.Embed(
            title="{LOADINGRED} Loading Profile...",
            color=0xFF0000
        )
        processing_msg = await ctx.send(embed=loading_embed)

        c.execute("SELECT * FROM badges WHERE user_id = ?", (member.id,))
        db_badges_data = c.fetchone()
        
        user_bot_badges = {}
        if db_badges_data:
            column_names = [desc[0] for desc in c.description]
            user_bot_badges = dict(zip(column_names, db_badges_data))
        
        # Default "Family" badge for everyone
        user_bot_badges['family'] = 1

        try:
            loop = asyncio.get_event_loop()
            file = await loop.run_in_executor(None, self.generate_profile_image, member, user_bot_badges)
        except Exception as e:
            error_embed = discord.Embed(
                title="Error", 
                description=f"Failed to create profile image: {e}",
                color=0xFF0000
            )
            return await processing_msg.edit(embed=error_embed)

        embed = discord.Embed(color=0xFF0000)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_author(name=f"◇ {member.name}'s Profile", icon_url=self.bot.user.display_avatar.url)
        
        description = (
            f"**◇ Account Created**: <t:{int(member.created_at.timestamp())}:D>\n"
            f"**◇ Joined Server**: <t:{int(member.joined_at.timestamp())}:D>\n"
            f"**◇ User ID**: `{member.id}`\n\n"
        )
        
        badge_list = []
        user = await self.bot.fetch_user(member.id)
        if user.banner or (user.avatar and user.avatar.is_animated()):
            badge_list.append(f"{DISCORD_BADGE_EMOJIS.get('nitro', '💎')} Nitro Subscriber")
        if member.premium_since:
            badge_list.append(f"{DISCORD_BADGE_EMOJIS.get('boost', '✨')} Server Booster")
            
        for flag in user.public_flags.all():
             if flag.name in DISCORD_BADGE_EMOJIS:
                badge_list.append(f"{DISCORD_BADGE_EMOJIS[flag.name]} {flag.name.replace('_', ' ').title()}")

        if badge_list:
            description += "**Official Badges:**\n" + "\n".join(badge_list)
        
        embed.description = description
        embed.set_image(url="attachment://profile.png")
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await processing_msg.delete()
        await ctx.send(embed=embed, file=file)

async def setup(client):
    if not hasattr(client, 'session'):
        client.session = aiohttp.ClientSession()
    await client.add_cog(Badges(client))
    
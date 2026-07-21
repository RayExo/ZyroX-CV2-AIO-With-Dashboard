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

# cogs/commands/ticket.py

import discord
from utils.emoji import CROSS, DELETE_ALT1, HANDSHAKE, LOCK, TICK, UNLOCK, ZBAN, ZMODULE, ZWRENCH
from discord import app_commands
from discord.ext import commands
import sqlite3
from datetime import datetime
import asyncio
import io
import os
import re
from utils.config import *

# --- Configurable Variables ---
EMBED_COLOR = 0xFF0000
TICKET_CHANNEL_IMAGE_URL = "https://cdn.discordapp.com/attachments/1403014653214330951/1403022431303630900/images_2.jpg?ex=68a1e776&is=68a095f6&hm=2c4e74b079fa409410920507bfb55549d485aafa89e194d15ab548eaba684555&"

# --- Emoji Variables ---
SUCCESS_EMOJI = TICK
ERROR_EMOJI = CROSS
LOCK_EMOJI = f"{UNLOCK} "
UNLOCK_EMOJI = LOCK
CLAIM_EMOJI = HANDSHAKE
CLOSE_EMOJI = ZBAN
DELETE_EMOJI = DELETE_ALT1
REOPEN_EMOJI = ZWRENCH
TRANSCRIPT_EMOJI = ZMODULE

# --- Constants ---
if not os.path.exists('db'):
    os.makedirs('db')
DB_PATH = 'db/ticket.db'
MAX_CATEGORIES = 15
TICKET_LIMIT_PER_USER = 3

# --- Database Class ---
class TicketDatabase:
    def __init__(self, path):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("CREATE TABLE IF NOT EXISTS guild_configs (guild_id INTEGER PRIMARY KEY, panel_channel_id INTEGER, logging_channel_id INTEGER, panel_message_id INTEGER, panel_type TEXT, embed_title TEXT, embed_description TEXT, embed_color INTEGER, embed_image_url TEXT, embed_thumbnail_url TEXT, closed_category_id INTEGER)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS ticket_categories (category_id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER, name TEXT NOT NULL, emoji TEXT, notified_roles TEXT, button_style INTEGER, discord_category_id INTEGER, FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id) ON DELETE CASCADE)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS open_tickets (channel_id INTEGER PRIMARY KEY, ticket_number INTEGER, guild_id INTEGER, creator_id INTEGER NOT NULL, category_db_id INTEGER, created_at TEXT NOT NULL, closed_by_id INTEGER, closed_at TEXT, is_locked BOOLEAN DEFAULT FALSE, is_claimed BOOLEAN DEFAULT FALSE, claimed_by_id INTEGER, FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id) ON DELETE CASCADE, FOREIGN KEY (category_db_id) REFERENCES ticket_categories(category_id) ON DELETE SET NULL)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS user_ticket_counts (guild_id INTEGER, user_id INTEGER, ticket_count INTEGER DEFAULT 0, PRIMARY KEY (guild_id, user_id))")

    def execute(self, q, p=()):
        with self.conn: return self.conn.execute(q, p)
    def fetchone(self, q, p=()):
        cur = self.conn.cursor(); cur.execute(q, p); return cur.fetchone()
    def fetchall(self, q, p=()):
        cur = self.conn.cursor(); cur.execute(q, p); return cur.fetchall()
    def close(self):
        if self.conn: self.conn.close()

# --- Utility Functions ---
async def get_or_create_log_channel(db, guild):
    config = db.fetchone("SELECT logging_channel_id FROM guild_configs WHERE guild_id = ?", (guild.id,))
    if config and config["logging_channel_id"] and (ch := guild.get_channel(config["logging_channel_id"])): return ch
    overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
    try:
        ch = await guild.create_text_channel(f"{BRAND_NAME}-ticket-logs", overwrites=overwrites)
        db.execute("INSERT INTO guild_configs (guild_id, logging_channel_id) VALUES (?,?) ON CONFLICT(guild_id) DO UPDATE SET logging_channel_id=excluded.logging_channel_id", (guild.id, ch.id))
        return ch
    except: return None

async def log_ticket_action(db, guild, user, action, details):
    if log_channel := await get_or_create_log_channel(db, guild):
        embed = discord.Embed(title=f"Ticket Action: {action}", color=EMBED_COLOR, timestamp=datetime.now())
        embed.add_field(name="Action By", value=user.mention).add_field(name="Details", value=details, inline=False)
        try: await log_channel.send(embed=embed)
        except: pass

async def get_or_create_closed_category(db, guild):
    config = db.fetchone("SELECT closed_category_id FROM guild_configs WHERE guild_id = ?", (guild.id,))
    if config and config["closed_category_id"] and (cat := guild.get_channel(config["closed_category_id"])): return cat
    overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
    try:
        cat = await guild.create_category("Closed Tickets", overwrites=overwrites)
        db.execute("UPDATE guild_configs SET closed_category_id = ? WHERE guild_id = ?", (cat.id, guild.id))
        return cat
    except: return None

# --- Setup Views ---
class EmbedEditorView(discord.ui.View):
    def __init__(self, cog, ctx, panel_channel, panel_type):
        super().__init__(timeout=600)
        self.cog, self.ctx, self.panel_channel, self.panel_type = cog, ctx, panel_channel, panel_type
        self.message = None
        self.embed_data = {"title": "Support Tickets", "description": "Click a button or select an option below to create a ticket.", "color": EMBED_COLOR}

    def _create_preview_embed(self):
        embed = discord.Embed.from_dict(self.embed_data)
        if img_url := self.embed_data.get("image", {}).get("url"): embed.set_image(url=img_url)
        if thumb_url := self.embed_data.get("thumbnail", {}).get("url"): embed.set_thumbnail(url=thumb_url)
        return embed

    async def start(self, interaction):
        await interaction.response.send_message("Use the buttons to customize the panel embed.", embed=self._create_preview_embed(), view=self, ephemeral=True)
        self.message = await interaction.original_response()

    async def _prompt(self, inter, prompt):
        await inter.response.send_message(prompt, ephemeral=True)
        try:
            msg = await self.cog.bot.wait_for("message", check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id, timeout=120)
            try: await msg.delete()
            except: pass
            return msg.content
        except: return None

    @discord.ui.button(label="Title", style=discord.ButtonStyle.green, row=0)
    async def edit_title(self, inter, button):
        if title := await self._prompt(inter, "Enter new title:"):
            self.embed_data["title"] = title
            await self.message.edit(embed=self._create_preview_embed())

    @discord.ui.button(label="Description", style=discord.ButtonStyle.green, row=0)
    async def edit_desc(self, inter, button):
        if desc := await self._prompt(inter, "Enter new description:"):
            self.embed_data["description"] = desc
            await self.message.edit(embed=self._create_preview_embed())
    
    @discord.ui.button(label="Image URL", style=discord.ButtonStyle.blurple, row=1)
    async def edit_image(self, inter, button):
        if url := await self._prompt(inter, "Enter image URL (`none` to remove):"):
            self.embed_data["image"] = {"url": url} if url.lower() != 'none' else {}
            await self.message.edit(embed=self._create_preview_embed())

    @discord.ui.button(label="Thumbnail URL", style=discord.ButtonStyle.blurple, row=1)
    async def edit_thumb(self, inter, button):
        if url := await self._prompt(inter, "Enter thumbnail URL (`none` to remove):"):
            self.embed_data["thumbnail"] = {"url": url} if url.lower() != 'none' else {}
            await self.message.edit(embed=self._create_preview_embed())

    @discord.ui.button(label="Submit & Continue", style=discord.ButtonStyle.primary, row=2)
    async def submit(self, inter, button):
        await inter.response.defer()
        for item in self.children: item.disabled = True
        try: await self.message.edit(view=self)
        except: pass
        self.cog.db.execute("INSERT INTO guild_configs (guild_id, panel_channel_id, panel_type, embed_title, embed_description, embed_color, embed_image_url, embed_thumbnail_url) VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(guild_id) DO UPDATE SET panel_channel_id=excluded.panel_channel_id, panel_type=excluded.panel_type, embed_title=excluded.embed_title, embed_description=excluded.embed_description, embed_color=excluded.embed_color, embed_image_url=excluded.embed_image_url, embed_thumbnail_url=excluded.embed_thumbnail_url", (self.ctx.guild.id, self.panel_channel.id, self.panel_type, self.embed_data["title"], self.embed_data["description"], self.embed_data["color"], self.embed_data.get("image",{}).get("url"), self.embed_data.get("thumbnail",{}).get("url")))
        await CategoryConfigView(self.cog, self.ctx).start(inter)
        self.stop()

class CategoryConfigView(discord.ui.View):
    def __init__(self, cog, ctx):
        super().__init__(timeout=900)
        self.cog, self.ctx, self.message, self.categories = cog, ctx, None, []
        self._setup_buttons()

    def _setup_buttons(self):
        panel_type = self.cog.db.fetchone("SELECT panel_type FROM guild_configs WHERE guild_id=?", (self.ctx.guild.id,))['panel_type']
        self.add_item(discord.ui.Button(label=f"Add Category", style=discord.ButtonStyle.success, custom_id="add_cat"))
        self.remove_select = discord.ui.Select(placeholder="Select a category to remove...", custom_id="remove_cat")
        self.add_item(self.remove_select)
        self.add_item(discord.ui.Button(label="Finish Setup", style=discord.ButtonStyle.primary, custom_id="finish_setup", row=2))

    async def start(self, interaction):
        self._update_remove_select()
        await interaction.followup.send(embed=self._update_embed(), view=self, ephemeral=True)
        self.message = await interaction.original_response()
    
    def _update_embed(self):
        embed = discord.Embed(title="Category Configuration", description="Add or remove ticket categories for your panel.", color=EMBED_COLOR)
        embed.add_field(name="Current Categories", value="\n".join([f"{c['emoji'] or ''} {c['name']}" for c in self.categories]) or "None yet. Click 'Add Category' to begin.")
        return embed

    def _update_remove_select(self):
        self.remove_select.options = [discord.SelectOption(label=c['name'], value=str(i), emoji=c.get('emoji')) for i, c in enumerate(self.categories)] or [discord.SelectOption(label="No categories to remove", value="placeholder")]

    async def _prompt(self, inter: discord.Interaction, prompt_text: str, followup: bool = False):
        send_method = inter.followup.send if followup else inter.response.send_message
        await send_method(prompt_text, ephemeral=True)
        try:
            msg = await self.cog.bot.wait_for("message", check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == inter.channel.id, timeout=120.0)
            try: await msg.delete()
            except discord.HTTPException: pass
            return msg.content
        except asyncio.TimeoutError:
            return None

    async def interaction_check(self, interaction):
        if interaction.user.id != self.ctx.author.id: return False
        custom_id = interaction.data["custom_id"]
        if custom_id == "add_cat": await self._add_category_flow(interaction)
        elif custom_id == "remove_cat": await self._remove_category(interaction, interaction.data["values"][0])
        elif custom_id == "finish_setup": await self._finish_setup(interaction)
        return True

    async def _add_category_flow(self, inter: discord.Interaction):
        await inter.response.defer()
        if len(self.categories) >= MAX_CATEGORIES:
            return await inter.followup.send(f"Max {MAX_CATEGORIES} categories reached.", ephemeral=True)

        cat_name = await self._prompt(inter, "Please type the name for the new category (e.g., General Support).", followup=True)
        if not cat_name: return await inter.followup.send("Timed out.", ephemeral=True)

        emoji = await self._prompt(inter, 'Please provide an emoji for the category, or type `skip`.', followup=True)
        if not emoji: return await inter.followup.send("Timed out.", ephemeral=True)
        if emoji.lower() == 'skip': emoji = None

        role_input = await self._prompt(inter, 'Please mention one or more staff roles to ping, separated by spaces (e.g., `@Ticket Support @Moderator`), or type `none`.', followup=True)
        if not role_input: return await inter.followup.send("Timed out.", ephemeral=True)
        
        role_ids = []
        if role_input.lower() != 'none':
            role_mentions = re.findall(r'<@&(\d+)>', role_input)
            for role_id_str in role_mentions:
                role_ids.append(int(role_id_str))
        
        self.categories.append({
            "name": cat_name, 
            "emoji": emoji,
            "notified_roles": ",".join(map(str, role_ids)) if role_ids else None, 
            "button_style": discord.ButtonStyle.secondary.value
        })
        self._update_remove_select()
        await self.message.edit(embed=self._update_embed(), view=self)
        await inter.followup.send(f"Category '{cat_name}' added/removed successfully.", ephemeral=True)

    async def _remove_category(self, inter, value):
        if value == "placeholder": return await inter.response.defer()
        try:
            idx = int(value)
            if 0 <= idx < len(self.categories):
                self.categories.pop(idx)
        except ValueError:
            pass
        self._update_remove_select()
        await self.message.edit(embed=self._update_embed(), view=self)
        await inter.response.defer()

    async def _finish_setup(self, inter):
        if not self.categories: return await inter.response.send_message("Add at least one category.", ephemeral=True)
        await inter.response.defer()
        db, guild_id = self.cog.db, self.ctx.guild.id
        db.execute("DELETE FROM ticket_categories WHERE guild_id = ?", (guild_id,))
        for cat in self.categories:
            try: cat_ch = await self.ctx.guild.create_category(f"{cat['name']} Tickets", overwrites={self.ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
            except: return await inter.followup.send(f"Can't create category for `{cat['name']}`.", ephemeral=True)
            db.execute('INSERT INTO ticket_categories (guild_id, name, emoji, notified_roles, button_style, discord_category_id) VALUES (?,?,?,?,?,?)', (guild_id,cat['name'],cat['emoji'],cat['notified_roles'],cat['button_style'],cat_ch.id))
        config = db.fetchone("SELECT * FROM guild_configs WHERE guild_id=?", (guild_id,))
        panel_ch = self.ctx.guild.get_channel(config['panel_channel_id'])
        panel_embed = discord.Embed(title=config['embed_title'], description=config['embed_description'], color=config['embed_color'])
        if img_url := config['embed_image_url']: panel_embed.set_image(url=img_url)
        if thumb_url := config['embed_thumbnail_url']: panel_embed.set_thumbnail(url=thumb_url)
        final_view = self.cog.create_panel_view(guild_id)
        msg = await panel_ch.send(embed=panel_embed, view=final_view)
        db.execute("UPDATE guild_configs SET panel_message_id = ? WHERE guild_id = ?", (msg.id, guild_id))
        await self.message.edit(content=f"{SUCCESS_EMOJI} Setup complete! Panel sent to {panel_ch.mention}.", view=None, embed=None)
        self.stop()

class TicketCog(commands.Cog, name="Ticket System"):
    def __init__(self, bot):
        self.bot, self.db = bot, TicketDatabase(DB_PATH)
        self.bot.loop.create_task(self.load_persistent_views())

    async def load_persistent_views(self):
        await self.bot.wait_until_ready()
        for config in self.db.fetchall("SELECT guild_id, panel_message_id FROM guild_configs WHERE panel_message_id IS NOT NULL"):
            if view := self.create_panel_view(config['guild_id']): self.bot.add_view(view, message_id=config['panel_message_id'])

    def create_panel_view(self, guild_id):
        config = self.db.fetchone("SELECT panel_type FROM guild_configs WHERE guild_id=?", (guild_id,))
        categories = self.db.fetchall("SELECT * FROM ticket_categories WHERE guild_id=?", (guild_id,))
        if not config or not categories: return None
        view_class = TicketPanelSelect if config['panel_type'] == 'dropdown' else TicketPanelButtons
        view = view_class(self)
        if config['panel_type'] == 'dropdown':
            view.children[0].options = [discord.SelectOption(label=c['name'], value=str(c['category_id']), emoji=c['emoji']) for c in categories]
        else:
            for c in categories: view.add_item(discord.ui.Button(label=c['name'], style=discord.ButtonStyle(c['button_style']), emoji=c['emoji'], custom_id=f"create_ticket_{c['category_id']}"))
        return view

    def cog_unload(self): self.db.close()

    @commands.Cog.listener()
    async def on_interaction(self, inter):
        if inter.type == discord.InteractionType.component and (cid := inter.data.get("custom_id","")).startswith("create_ticket_"): await self.create_ticket_flow(inter, int(cid.split("_")[-1]))

    async def create_ticket_flow(self, inter, cat_id):
        await inter.response.defer(ephemeral=True)
        guild, user = inter.guild, inter.user
        if (count := self.db.fetchone("SELECT ticket_count FROM user_ticket_counts WHERE guild_id=? AND user_id=?",(guild.id,user.id))) and count['ticket_count'] >= TICKET_LIMIT_PER_USER: return await inter.followup.send(f"You have reached the max of {TICKET_LIMIT_PER_USER} open tickets.",ephemeral=True)
        
        cat_info = self.db.fetchone("SELECT * FROM ticket_categories WHERE category_id=?", (cat_id,))
        disc_cat = guild.get_channel(cat_info['discord_category_id'])
        if not cat_info or not disc_cat: return await inter.followup.send("This ticket category has been deleted or is misconfigured.", ephemeral=True)
        
        t_num = (self.db.fetchone("SELECT MAX(ticket_number) as n FROM open_tickets WHERE guild_id=?", (guild.id,))['n'] or 0) + 1
        
        overwrites = {guild.default_role:discord.PermissionOverwrite(view_channel=False), user:discord.PermissionOverwrite(view_channel=True), guild.me:discord.PermissionOverwrite(view_channel=True, manage_channels=True)}
        
        pings = [user.mention]
        if cat_info['notified_roles']:
            for role_id in cat_info['notified_roles'].split(','):
                if role := guild.get_role(int(role_id)):
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True)
                    pings.append(role.mention)
        
        try: ch = await disc_cat.create_text_channel(name=f"ticket-{t_num:04d}-{user.name.lower()}", overwrites=overwrites)
        except: return await inter.followup.send("I lack permissions to create a channel.", ephemeral=True)
        
        self.db.execute('INSERT INTO open_tickets VALUES (?,?,?,?,?,?,?,?,?,?,?)', (ch.id,t_num,guild.id,user.id,cat_id,datetime.now().isoformat(),None,None,False,False,None))
        self.db.execute('INSERT INTO user_ticket_counts VALUES (?,?,1) ON CONFLICT(guild_id,user_id) DO UPDATE SET ticket_count=ticket_count+1', (guild.id,user.id))
        await log_ticket_action(self.db, guild, user, "Ticket Created", f"Ticket {ch.mention} by {user.mention} (Category: {cat_info['name']}).")
        
        ticket_embed = discord.Embed(title=f"Welcome to your Ticket ( #{t_num:04d} )", description="Thank you for reaching out for support. Our staff team has been notified and will be with you as soon as possible.\n\nPlease describe your issue in detail while you wait.", color=EMBED_COLOR)
        ticket_embed.set_image(url=TICKET_CHANNEL_IMAGE_URL)
        await ch.send(content=" ".join(pings), embed=ticket_embed, view=TicketActionsView(self, ch.id, cat_id))
        await inter.followup.send(f"Your ticket has been successfully created: {ch.mention}", ephemeral=True)

    @commands.hybrid_group(name="ticket", description="Main command group for the ticket system.")
    @commands.guild_only()
    async def ticket(self, ctx):
        if ctx.invoked_subcommand is None: await ctx.send_help(ctx.command)

    @ticket.command(name="setup", description="Start the interactive setup for the ticket panel.")
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(style="The style of the ticket creation panel.", channel="The channel where the ticket panel will be sent.")
    @app_commands.choices(style=[app_commands.Choice(name="Dropdown Menu", value="dropdown"), app_commands.Choice(name="Buttons", value="button")])
    async def setup(self, ctx, style: app_commands.Choice[str], channel: discord.TextChannel):
        await EmbedEditorView(self, ctx, channel, style.value).start(ctx.interaction)

    @ticket.command(name="close", description="Close the current ticket channel.")
    @commands.has_permissions(manage_channels=True)
    async def close(self, ctx): await self._dispatch_action(ctx, "close")
    
    @ticket.command(name="lock", description="Lock the ticket, preventing the user from sending messages.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx): await self._dispatch_action(ctx, "lock")
    
    @ticket.command(name="unlock", description="Unlock the ticket, allowing the user to send messages again.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx): await self._dispatch_action(ctx, "unlock")
    
    @ticket.command(name="claim", description="Claim the ticket to notify others that you are handling it.")
    @commands.has_permissions(manage_channels=True)
    async def claim(self, ctx): await self._dispatch_action(ctx, "claim")

    @ticket.command(name="transcript", description="Generate a transcript of a closed ticket.")
    @commands.has_permissions(manage_channels=True)
    async def transcript(self, ctx):
        if not ctx.interaction: return await ctx.send("Please use the slash command version of this command.")
        await ClosedTicketActionsView(self, ctx.channel.id)._generate_transcript(ctx.interaction, False)

class TicketPanelSelect(discord.ui.View):
    def __init__(self, cog): super().__init__(timeout=None); self.cog = cog
    @discord.ui.select(placeholder="Select a category to open a ticket...", custom_id="ticket_panel_select")
    async def select_ticket(self, inter, select): await self.cog.create_ticket_flow(inter, int(select.values[0]))

class TicketPanelButtons(discord.ui.View):
    def __init__(self, cog): super().__init__(timeout=None); self.cog = cog

class TicketActionsView(discord.ui.View):
    def __init__(self, cog, ch_id, cat_id):
        super().__init__(timeout=None)
        self.cog, self.ch_id, self.cat_id = cog, ch_id, cat_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        cat_info = self.cog.db.fetchone("SELECT notified_roles FROM ticket_categories WHERE category_id=?", (self.cat_id,))
        if not cat_info or not cat_info['notified_roles']:
            await interaction.response.send_message("This ticket is misconfigured; no staff roles are assigned.", ephemeral=True)
            return False
        
        allowed_role_ids = {int(r_id) for r_id in cat_info['notified_roles'].split(',')}
        user_role_ids = {role.id for role in interaction.user.roles}
        
        if not user_role_ids.intersection(allowed_role_ids):
            await interaction.response.send_message("You do not have the required role to perform this action.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Lock", emoji=LOCK_EMOJI, custom_id="t_lock", style=discord.ButtonStyle.secondary)
    async def b_lock(self, i, b):
        t = self.cog.db.fetchone("SELECT * FROM open_tickets WHERE channel_id=?", (self.ch_id,))
        if t['is_locked']: return await i.response.send_message("This ticket is already locked.", ephemeral=True)
        creator = i.guild.get_member(t['creator_id'])
        if creator: await i.channel.set_permissions(creator, send_messages=False)
        self.cog.db.execute("UPDATE open_tickets SET is_locked=1 WHERE channel_id=?", (self.ch_id,))
        await i.response.send_message(f"{LOCK_EMOJI} Ticket locked by {i.user.mention}.")
        await log_ticket_action(self.cog.db, i.guild, i.user, "Locked", f"{i.channel.mention}")

    @discord.ui.button(label="Unlock", emoji=UNLOCK_EMOJI, custom_id="t_unlock", style=discord.ButtonStyle.secondary)
    async def b_unlock(self, i, b):
        t = self.cog.db.fetchone("SELECT * FROM open_tickets WHERE channel_id=?", (self.ch_id,))
        if not t['is_locked']: return await i.response.send_message("This ticket is already unlocked.", ephemeral=True)
        creator = i.guild.get_member(t['creator_id'])
        if creator: await i.channel.set_permissions(creator, send_messages=True)
        self.cog.db.execute("UPDATE open_tickets SET is_locked=0 WHERE channel_id=?", (self.ch_id,))
        await i.response.send_message(f"{UNLOCK_EMOJI} Ticket unlocked by {i.user.mention}.")
        await log_ticket_action(self.cog.db, i.guild, i.user, "Unlocked", f"{i.channel.mention}")

    @discord.ui.button(label="Claim", emoji=CLAIM_EMOJI, custom_id="t_claim", style=discord.ButtonStyle.primary)
    async def b_claim(self, i, b):
        t = self.cog.db.fetchone("SELECT * FROM open_tickets WHERE channel_id=?", (self.ch_id,))
        if t['is_claimed']: return await i.response.send_message(f"This ticket is already claimed by <@{t['claimed_by_id']}>.", ephemeral=True)
        self.cog.db.execute("UPDATE open_tickets SET is_claimed=1, claimed_by_id=? WHERE channel_id=?", (i.user.id, self.ch_id))
        await i.response.send_message(f"{CLAIM_EMOJI} Ticket claimed by {i.user.mention}. They will now handle this request.")
        await log_ticket_action(self.cog.db, i.guild, i.user, "Claimed", f"{i.channel.mention}")

    @discord.ui.button(label="Close", emoji=CLOSE_EMOJI, style=discord.ButtonStyle.danger, custom_id="t_close")
    async def b_close(self, i, b):
        await i.response.defer(ephemeral=True)
        t = self.cog.db.fetchone("SELECT * FROM open_tickets WHERE channel_id=?", (self.ch_id,))
        creator = i.guild.get_member(t['creator_id'])
        if creator:
            self.cog.db.execute("UPDATE user_ticket_counts SET ticket_count=MAX(0,ticket_count-1) WHERE guild_id=? AND user_id=?", (i.guild.id, creator.id))
            await i.channel.set_permissions(creator, send_messages=False, view_channel=False)
        
        category_info = self.cog.db.fetchone("SELECT name FROM ticket_categories WHERE category_id=?", (self.cat_id,))
        category_name = category_info['name'] if category_info else "Unknown"

        closed_category = await get_or_create_closed_category(self.cog.db, i.guild)
        if closed_category: await i.channel.edit(category=closed_category)
        
        self.cog.db.execute("UPDATE open_tickets SET closed_by_id=?, closed_at=? WHERE channel_id=?", (i.user.id, datetime.now().isoformat(), self.ch_id))
        await log_ticket_action(self.cog.db, i.guild, i.user, "Closed", f"Ticket {i.channel.mention} (Category: {category_name})")
        
        closed_embed = discord.Embed(
            title="Ticket Closed",
            description=f"This ticket has been officially closed and archived by {i.user.mention}.\nThe user has been removed from the channel.\n\nStaff can use the buttons below to reopen, create a transcript, or permanently delete the channel.",
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        closed_embed.add_field(name="Ticket Creator", value=f"<@{t['creator_id']}>", inline=True)
        closed_embed.add_field(name="Closed By", value=i.user.mention, inline=True)
        closed_embed.add_field(name="Original Category", value=category_name, inline=True)
        
        await i.channel.send(embed=closed_embed, view=ClosedTicketActionsView(self.cog, self.ch_id, self.cat_id))
        await i.message.edit(view=None)
        await i.followup.send("Ticket successfully closed and archived.", ephemeral=True)
        self.stop()

class ClosedTicketActionsView(discord.ui.View):
    def __init__(self, cog, ch_id, cat_id):
        super().__init__(timeout=None)
        self.cog, self.ch_id, self.cat_id = cog, ch_id, cat_id
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        cat_info = self.cog.db.fetchone("SELECT notified_roles FROM ticket_categories WHERE category_id=?", (self.cat_id,))
        if not cat_info or not cat_info['notified_roles']: return False
        allowed_role_ids = {int(r_id) for r_id in cat_info['notified_roles'].split(',')}
        user_role_ids = {role.id for role in interaction.user.roles}
        if not user_role_ids.intersection(allowed_role_ids):
            await interaction.response.send_message("You do not have the required role for this action.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Reopen", emoji=REOPEN_EMOJI, style=discord.ButtonStyle.success)
    async def b_reopen(self, i: discord.Interaction, button: discord.ui.Button):
        await i.response.defer(ephemeral=True)
        t = self.cog.db.fetchone("SELECT * FROM open_tickets WHERE channel_id=?", (self.ch_id,))
        cat_info = self.cog.db.fetchone("SELECT discord_category_id FROM ticket_categories WHERE category_id=?", (self.cat_id,))
        
        original_category = i.guild.get_channel(cat_info['discord_category_id'])
        if original_category: await i.channel.edit(category=original_category)

        creator = i.guild.get_member(t['creator_id'])
        if creator:
            await i.channel.set_permissions(creator, view_channel=True, send_messages=True)
            self.cog.db.execute("INSERT INTO user_ticket_counts VALUES (?,?,1) ON CONFLICT(guild_id,user_id) DO UPDATE SET ticket_count=ticket_count+1", (i.guild.id, creator.id))
        
        self.cog.db.execute("UPDATE open_tickets SET closed_by_id=NULL, closed_at=NULL WHERE channel_id=?", (self.ch_id,))
        
        reopen_embed = discord.Embed(title="Ticket Reopened", description=f"This ticket has been reopened by {i.user.mention}.", color=EMBED_COLOR)
        await i.channel.send(embed=reopen_embed, view=TicketActionsView(self.cog, self.ch_id, self.cat_id))
        await i.message.edit(view=None)
        await log_ticket_action(self.cog.db, i.guild, i.user, "Reopened", f"{i.channel.mention}")
        self.stop()
        
    @discord.ui.button(label="Transcript", emoji=TRANSCRIPT_EMOJI, style=discord.ButtonStyle.primary)
    async def b_transcript(self, i, b): await self._generate_transcript(i, False)

    @discord.ui.button(label="Delete", emoji=DELETE_EMOJI, style=discord.ButtonStyle.danger)
    async def b_delete(self, i, b): await self._generate_transcript(i, True)

    async def _generate_transcript(self, i, delete_after):
        await i.response.defer(ephemeral=True, thinking=True)
        ch = i.guild.get_channel(self.ch_id)
        if not ch: return await i.followup.send("Channel not found.", ephemeral=True)
        
        messages = [m async for m in ch.history(limit=None, oldest_first=True)]
        content = f"Transcript for ticket #{ch.name} in {i.guild.name}\n\n"
        for m in messages:
            content += f"[{m.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {m.author.display_name}: {m.clean_content}\n"
            for attachment in m.attachments: content += f"  [Attachment: {attachment.url}]\n"
        file = discord.File(io.BytesIO(content.encode()), filename=f"transcript-{ch.name}.txt")

        try:
            await i.user.send(f"Transcript for ticket {ch.mention} in {i.guild.name}:", file=file)
            await i.followup.send(f"Transcript sent to your DMs.", ephemeral=True)
        except: await i.followup.send("Could not DM you the transcript. Do you have DMs disabled?", file=file, ephemeral=True)
        
        if delete_after:
            await i.followup.send("This ticket channel will be permanently deleted in 10 seconds...", ephemeral=True)
            await log_ticket_action(self.cog.db, i.guild, i.user, "Deletion Scheduled", f"{ch.mention}")
            await asyncio.sleep(10)
            await ch.delete()
            self.cog.db.execute("DELETE FROM open_tickets WHERE channel_id=?", (self.ch_id,))

async def setup(bot):
    await bot.add_cog(TicketCog(bot))

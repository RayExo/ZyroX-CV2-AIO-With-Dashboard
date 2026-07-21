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
from discord import ui, SelectOption
from discord.ui import LayoutView, TextDisplay, Separator, ActionRow
import aiosqlite
import asyncio
from typing import Dict, List, Optional
from utils.cv2 import CV2, build_container

class JoinToCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.private_channels: Dict[int, Dict] = {}
        self.category_name = "J2C"
        self.setup_data: Dict[int, Dict] = {}
        self.db_path = "j2c_data.db"
        self.blocked_users: Dict[int, List[int]] = {}  # {vc_id: [user_ids]}
        self.creating_vc = set()

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_setup (
                    guild_id INTEGER PRIMARY KEY,
                    join_channel_id INTEGER,
                    control_channel_id INTEGER,
                    control_message_id INTEGER,
                    category_id INTEGER
                )
            """)
            try:
                await db.execute("ALTER TABLE guild_setup ADD COLUMN category_id INTEGER")
            except aiosqlite.OperationalError:
                pass
            await db.execute("""
                CREATE TABLE IF NOT EXISTS private_channels (
                    vc_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    owner_id INTEGER,
                    member_limit INTEGER DEFAULT 2,
                    region TEXT DEFAULT '',
                    is_locked BOOLEAN DEFAULT FALSE,
                    has_waiting_room BOOLEAN DEFAULT FALSE,
                    has_thread BOOLEAN DEFAULT FALSE
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS blocked_users (
                    vc_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (vc_id, user_id)
                )
            """)
            await db.commit()

    async def load_data(self):
        async with aiosqlite.connect(self.db_path) as db:
            # Load guild setups
            async with db.execute("SELECT guild_id, join_channel_id, control_channel_id, control_message_id, category_id FROM guild_setup") as cursor:
                async for row in cursor:
                    guild_id, join_channel_id, control_channel_id, control_message_id, category_id = row
                    self.setup_data[guild_id] = {
                        "join_channel_id": join_channel_id,
                        "control_channel_id": control_channel_id,
                        "control_message_id": control_message_id,
                        "category_id": category_id
                    }

            # Load private channels
            async with db.execute("SELECT * FROM private_channels") as cursor:
                async for row in cursor:
                    vc_id, guild_id, owner_id, member_limit, region, is_locked, has_waiting_room, has_thread = row
                    self.private_channels[vc_id] = {
                        "owner": owner_id,
                        "limit": member_limit,
                        "region": region,
                        "is_locked": bool(is_locked),
                        "has_waiting_room": bool(has_waiting_room),
                        "has_thread": bool(has_thread),
                        "guild_id": guild_id
                    }

            # Load blocked users
            async with db.execute("SELECT * FROM blocked_users") as cursor:
                async for row in cursor:
                    vc_id, user_id = row
                    if vc_id not in self.blocked_users:
                        self.blocked_users[vc_id] = []
                    self.blocked_users[vc_id].append(user_id)

    async def save_guild_setup(self, guild_id: int, data: Dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO guild_setup (guild_id, join_channel_id, control_channel_id, control_message_id, category_id)
                VALUES (?, ?, ?, ?, ?)
            """, (guild_id, data["join_channel_id"], data["control_channel_id"], data["control_message_id"], data.get("category_id")))
            await db.commit()

    async def save_private_channel(self, vc_id: int, guild_id: int, data: Dict):
        try:
            if vc_id not in self.private_channels:
                self.private_channels[vc_id] = data
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO private_channels 
                    (vc_id, guild_id, owner_id, member_limit, region, is_locked, has_waiting_room, has_thread)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vc_id, guild_id, 
                    data["owner"], 
                    data.get("limit", 2),
                    data.get("region", ""),
                    data.get("is_locked", False),
                    data.get("has_waiting_room", False),
                    data.get("has_thread", False)
                ))
                await db.commit()
        except Exception as e:
            print(f"Error saving private channel: {e}")

    async def delete_private_channel(self, vc_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM private_channels WHERE vc_id = ?", (vc_id,))
            await db.execute("DELETE FROM blocked_users WHERE vc_id = ?", (vc_id,))
            await db.commit()

    async def delete_guild_setup(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM guild_setup WHERE guild_id = ?", (guild_id,))
            await db.execute("DELETE FROM private_channels WHERE guild_id = ?", (guild_id,))
            await db.execute("DELETE FROM blocked_users WHERE vc_id IN (SELECT vc_id FROM private_channels WHERE guild_id = ?)", (guild_id,))
            await db.commit()

    async def block_user(self, vc_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO blocked_users (vc_id, user_id) VALUES (?, ?)", (vc_id, user_id))
            await db.commit()
        if vc_id not in self.blocked_users:
            self.blocked_users[vc_id] = []
        if user_id not in self.blocked_users[vc_id]:
            self.blocked_users[vc_id].append(user_id)

    async def unblock_user(self, vc_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM blocked_users WHERE vc_id = ? AND user_id = ?", (vc_id, user_id))
            await db.commit()
        if vc_id in self.blocked_users and user_id in self.blocked_users[vc_id]:
            self.blocked_users[vc_id].remove(user_id)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.init_db()
        await self.load_data()
        for guild_id, data in self.setup_data.items():
            guild = self.bot.get_guild(guild_id)
            if guild:
                try:
                    control_channel = guild.get_channel(data["control_channel_id"])
                    if control_channel:
                        msg = None
                        if data["control_message_id"]:
                            try:
                                msg = await control_channel.fetch_message(data["control_message_id"])
                            except:
                                pass
                        
                        if msg:
                            view = ControlPanelView(self, guild)
                            await msg.edit(view=view, embed=None, content=None)
                        else:
                            view = ControlPanelView(self, guild)
                            msg = await control_channel.send(view=view)
                            self.setup_data[guild_id]["control_message_id"] = msg.id
                            await self.save_guild_setup(guild_id, self.setup_data[guild_id])
                except Exception as e:
                    print(f"Error in J2C on_ready: {e}")
                    continue

    @commands.command(name='j2csetup')
    @commands.has_permissions(administrator=True)
    async def setup_private_channels(self, ctx):
        if ctx.guild.id in self.setup_data:
            await ctx.send(view=CV2("❌ Error", "J2C system is already setup in this server!"))
            return
            
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if not category:
            category = await ctx.guild.create_category(self.category_name)
        
        join_channel = await ctx.guild.create_voice_channel(
            "➕ Join to Create",
            category=category,
            reason="J2C System Setup"
        )
        
        control_channel = await ctx.guild.create_text_channel(
            "ctrl-panel",
            category=category,
            reason="J2C System Setup"
        )
        
        view = ControlPanelView(self, ctx.guild)
        control_message = await control_channel.send(view=view)
        
        self.setup_data[ctx.guild.id] = {
            "join_channel_id": join_channel.id,
            "control_channel_id": control_channel.id,
            "control_message_id": control_message.id
        }
        await self.save_guild_setup(ctx.guild.id, self.setup_data[ctx.guild.id])
        
        await ctx.send(view=CV2("✅ Success", f"J2C system setup complete! Join {join_channel.mention} to create a private VC."))

    @commands.command(name='j2creset')
    @commands.has_permissions(administrator=True)
    async def reset_private_channels(self, ctx):
        if ctx.guild.id not in self.setup_data:
            await ctx.send(view=CV2("❌ Error", "J2C system is not setup in this server!"))
            return
            
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if category:
            for channel in category.channels:
                try:
                    await channel.delete(reason="J2C System Reset")
                except:
                    continue
        
        if category:
            try:
                await category.delete(reason="J2C System Reset")
            except:
                pass
        
        vc_ids = [vc_id for vc_id, data in self.private_channels.items() 
                 if data.get("guild_id") == ctx.guild.id]
        for vc_id in vc_ids:
            del self.private_channels[vc_id]
        
        del self.setup_data[ctx.guild.id]
        await self.delete_guild_setup(ctx.guild.id)
        
        await ctx.send(view=CV2("✅ Success", "J2C system has been completely reset in this server!"))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id not in self.setup_data:
            return
            
        guild_data = self.setup_data[member.guild.id]
        
        # User joined the join channel
        if after.channel and after.channel.id == guild_data["join_channel_id"]:
            if member.id in self.creating_vc:
                return
            self.creating_vc.add(member.id)
            try:
                category_id = guild_data.get("category_id")
                category = None
                if category_id:
                    try:
                        category = member.guild.get_channel(int(category_id))
                    except:
                        pass
                
                # Fallback 1: Use the parent category of the join channel
                if not category and after.channel.category:
                    category = after.channel.category
                    
                # Fallback 2: J2C category by name
                if not category:
                    category = discord.utils.get(member.guild.categories, name=self.category_name)
                    
                vc = await member.guild.create_voice_channel(
                    f"{member.name}'s VC",
                    category=category,
                    reason="Private VC Creation",
                    user_limit=2
                )
                
                await member.move_to(vc)
                
                self.private_channels[vc.id] = {
                    "owner": member.id,
                    "limit": 2,
                    "region": "",
                    "is_locked": False,
                    "has_waiting_room": False,
                    "has_thread": False,
                    "guild_id": member.guild.id
                }
                await self.save_private_channel(vc.id, member.guild.id, self.private_channels[vc.id])
                await self.update_control_panel(member.guild)
            finally:
                self.creating_vc.discard(member.id)
            
        # User left a private channel
        if before.channel and before.channel.id in self.private_channels:
            # Check if user was blocked
            if (before.channel.id in self.blocked_users and 
                member.id in self.blocked_users[before.channel.id]):
                await member.move_to(None)
                return
                
            # Check if channel is empty
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                except:
                    pass
                
                if before.channel.id in self.private_channels:
                    del self.private_channels[before.channel.id]
                    await self.delete_private_channel(before.channel.id)
                
                await self.update_control_panel(member.guild)

    async def update_control_panel(self, guild: discord.Guild):
        if guild.id not in self.setup_data:
            return
            
        guild_data = self.setup_data[guild.id]
        control_channel = guild.get_channel(guild_data["control_channel_id"])
        if not control_channel or not guild_data["control_message_id"]:
            return
            
        try:
            control_message = await control_channel.fetch_message(guild_data["control_message_id"])
            view = ControlPanelView(self, guild)
            await control_message.edit(view=view, embed=None, content=None)
        except:
            pass

class ControlPanelView(LayoutView):
    def __init__(self, cog, guild):
        super().__init__(timeout=None)
        self.cog = cog
        
        desc = ("Join the 'Join to Create VC' voice channel to create your own private voice channel.\n\n"
               "Use the buttons below to manage your private VC.")
        active_vcs = []
        for vc_id, data in self.cog.private_channels.items():
            if guild.get_channel(vc_id):
                owner = guild.get_member(data["owner"])
                if owner:
                    status = []
                    if data["is_locked"]:
                        status.append("🔒 Locked")
                    if data["has_thread"]:
                        status.append("💬 Thread")
                    
                    vc_info = f"<#{vc_id}> (👑 {owner.mention})"
                    if status:
                        vc_info += f" [{' '.join(status)}]"
                    active_vcs.append(vc_info)
        
        if active_vcs:
            desc += "\n\n**Active Private VCs**\n" + "\n".join(active_vcs)
            
        container = build_container(
            TextDisplay("**J2C System**"),
            Separator(visible=True),
            TextDisplay(desc)
        )
        self.add_item(container)

        b_limit = ui.Button(label="LIMIT", style=discord.ButtonStyle.blurple, custom_id="j2c:limit", emoji="⏳")
        b_limit.callback = self.set_limit
        b_privacy = ui.Button(label="PRIVACY", style=discord.ButtonStyle.blurple, custom_id="j2c:privacy", emoji="🔒")
        b_privacy.callback = self.toggle_privacy
        b_thread = ui.Button(label="THREAD", style=discord.ButtonStyle.blurple, custom_id="j2c:thread", emoji="💬")
        b_thread.callback = self.create_thread
        b_untrust = ui.Button(label="UNTRUST", style=discord.ButtonStyle.green, custom_id="j2c:untrust", emoji="❌")
        b_untrust.callback = self.untrust
        b_invite = ui.Button(label="INVITE", style=discord.ButtonStyle.green, custom_id="j2c:invite", emoji="✉️")
        b_invite.callback = self.invite_user
        b_kick = ui.Button(label="KICK", style=discord.ButtonStyle.green, custom_id="j2c:kick", emoji="👢")
        b_kick.callback = self.kick_user
        b_region = ui.Button(label="REGION", style=discord.ButtonStyle.green, custom_id="j2c:region", emoji="🌍")
        b_region.callback = self.set_region
        b_unblock = ui.Button(label="UNBLOCK", style=discord.ButtonStyle.red, custom_id="j2c:unblock", emoji="🔓")
        b_unblock.callback = self.unblock
        b_claim = ui.Button(label="CLAIM", style=discord.ButtonStyle.red, custom_id="j2c:claim", emoji="⭐")
        b_claim.callback = self.claim
        b_transfer = ui.Button(label="TRANSFER", style=discord.ButtonStyle.red, custom_id="j2c:transfer", emoji="🔄")
        b_transfer.callback = self.transfer
        b_delete = ui.Button(label="DELETE", style=discord.ButtonStyle.red, custom_id="j2c:delete", emoji="🗑️")
        b_delete.callback = self.delete_vc
        b_block = ui.Button(label="BLOCK", style=discord.ButtonStyle.danger, custom_id="j2c:block", emoji="🚫")
        b_block.callback = self.block

        self.add_item(ActionRow(b_limit, b_privacy, b_thread))
        self.add_item(ActionRow(b_untrust, b_invite, b_kick, b_region))
        self.add_item(ActionRow(b_unblock, b_claim, b_transfer, b_delete))
        self.add_item(ActionRow(b_block))
    
    async def get_owned_vc(self, interaction: discord.Interaction) -> Optional[discord.VoiceChannel]:
        for vc_id, data in self.cog.private_channels.items():
            if data["owner"] == interaction.user.id:
                vc = interaction.guild.get_channel(vc_id)
                if vc:
                    return vc
        return None
    
    async def set_limit(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("You don't own any private VC!", ephemeral=True)
            return
        modal = SetLimitModal(vc)
        await interaction.response.send_modal(modal)
    
    async def toggle_privacy(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.followup.send("You don't own any private VC!", ephemeral=True)
            return
        is_locked = not self.cog.private_channels[vc.id]["is_locked"]
        await vc.set_permissions(interaction.guild.default_role, connect=not is_locked)
        self.cog.private_channels[vc.id]["is_locked"] = is_locked
        await self.cog.save_private_channel(vc.id, interaction.guild.id, self.cog.private_channels[vc.id])
        await interaction.followup.send(f"VC is now {'🔒 locked' if is_locked else '🔓 unlocked'}!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)

    
    async def create_thread(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.followup.send("You don't own any private VC!", ephemeral=True)
            return
        has_thread = not self.cog.private_channels[vc.id]["has_thread"]
        self.cog.private_channels[vc.id]["has_thread"] = has_thread
        await self.cog.save_private_channel(vc.id, interaction.guild.id, self.cog.private_channels[vc.id])
        if has_thread:
            thread = await interaction.channel.create_thread(name=f"{vc.name} Discussion", auto_archive_duration=60)
            await interaction.followup.send(f"Created thread: {thread.mention}", ephemeral=True)
        else:
            await interaction.followup.send("Thread feature disabled for your VC", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)
    
    async def untrust(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.followup.send("You don't own any private VC!", ephemeral=True)
            return
        await interaction.followup.send("Untrust feature would be implemented here", ephemeral=True)
    
    async def invite_user(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("You don't own any private VC!", ephemeral=True)
            return
        options = []
        for member in interaction.guild.members:
            if (member not in vc.members and not member.bot and member != interaction.user):
                options.append(SelectOption(label=member.name, value=str(member.id)))
        if not options:
            await interaction.response.send_message("No members available to invite!", ephemeral=True)
            return
        dropdown = UserSelectDropdown(options, "Select members to invite", self.invite_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Select members to invite:", view=view, ephemeral=True)
    
    async def invite_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc: return
        for user_id in selected:
            member = interaction.guild.get_member(int(user_id))
            if member:
                try: await member.send(f"You've been invited to join {vc.mention} by {interaction.user.mention}!")
                except: pass
        await interaction.followup.send("Invites sent!", ephemeral=True)
    
    async def kick_user(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("You don't own any private VC!", ephemeral=True)
            return
        options = []
        for member in vc.members:
            if member.id != interaction.user.id:
                options.append(SelectOption(label=member.name, value=str(member.id)))
        if not options:
            await interaction.response.send_message("No users to kick in your VC!", ephemeral=True)
            return
        dropdown = UserSelectDropdown(options, "Select members to kick", self.kick_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Select members to kick:", view=view, ephemeral=True)
    
    async def kick_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc: return
        for user_id in selected:
            member = interaction.guild.get_member(int(user_id))
            if member and member in vc.members:
                try: await member.move_to(None)
                except: pass
        await interaction.followup.send("Selected members kicked!", ephemeral=True)
    
    async def set_region(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("You don't own any private VC!", ephemeral=True)
            return
        regions = [
            SelectOption(label="Automatic", value="auto"), SelectOption(label="US West", value="us-west"),
            SelectOption(label="US East", value="us-east"), SelectOption(label="Europe", value="europe"),
            SelectOption(label="Singapore", value="singapore"), SelectOption(label="Japan", value="japan"),
            SelectOption(label="Brazil", value="brazil"), SelectOption(label="Australia", value="australia")
        ]
        dropdown = RegionSelectDropdown(regions, vc)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Select a region:", view=view, ephemeral=True)
    
    async def unblock(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("You don't own any private VC!", ephemeral=True)
            return
        if vc.id not in self.cog.blocked_users or not self.cog.blocked_users[vc.id]:
            await interaction.response.send_message("No blocked users!", ephemeral=True)
            return
        options = []
        for user_id in self.cog.blocked_users[vc.id]:
            member = interaction.guild.get_member(user_id)
            if member:
                options.append(SelectOption(label=member.name, value=str(user_id)))
        dropdown = UserSelectDropdown(options, "Select users to unblock", self.unblock_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Select users to unblock:", view=view, ephemeral=True)
    
    async def unblock_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc: return
        for user_id in selected:
            await self.cog.unblock_user(vc.id, int(user_id))
        await interaction.followup.send("Selected users unblocked!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)
    
    async def claim(self, interaction: discord.Interaction):
        available_vcs = []
        for vc_id, data in self.cog.private_channels.items():
            if data["guild_id"] == interaction.guild.id:
                vc = interaction.guild.get_channel(vc_id)
                if vc:
                    owner = interaction.guild.get_member(data["owner"])
                    if not owner or owner not in vc.members:
                        available_vcs.append((vc, data))
        if not available_vcs:
            await interaction.response.send_message("No VCs available to claim!", ephemeral=True)
            return
        options = []
        for vc, data in available_vcs:
            owner_mention = f"<{data['owner']}>" if data['owner'] else "Unknown"
            options.append(SelectOption(label=f"{vc.name} (prev: {owner_mention})", value=str(vc.id)))
        dropdown = VCSelectDropdown(options, "Select VC to claim", self.claim_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Select VC to claim:", view=view, ephemeral=True)
    
    async def claim_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc_id = int(selected[0])
        vc = interaction.guild.get_channel(vc_id)
        if not vc:
            await interaction.followup.send("VC no longer exists!", ephemeral=True)
            return
        self.cog.private_channels[vc.id]["owner"] = interaction.user.id
        await self.cog.save_private_channel(vc.id, interaction.guild.id, self.cog.private_channels[vc.id])
        await interaction.followup.send(f"You've claimed {vc.mention}!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)
    
    async def transfer(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("You don't own any private VC!", ephemeral=True)
            return
        options = []
        for member in vc.members:
            if member.id != interaction.user.id:
                options.append(SelectOption(label=member.name, value=str(member.id)))
        if not options:
            await interaction.response.send_message("No users to transfer to in your VC!", ephemeral=True)
            return
        dropdown = UserSelectDropdown(options, "Select new owner", self.transfer_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Select new owner:", view=view, ephemeral=True)
    
    async def transfer_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc: return
        new_owner_id = int(selected[0])
        new_owner = interaction.guild.get_member(new_owner_id)
        if not new_owner:
            await interaction.followup.send("User not found!", ephemeral=True)
            return
        self.cog.private_channels[vc.id]["owner"] = new_owner_id
        await self.cog.save_private_channel(vc.id, interaction.guild.id, self.cog.private_channels[vc.id])
        await interaction.followup.send(f"Transferred ownership of {vc.mention} to {new_owner.mention}!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)
    
    async def delete_vc(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.followup.send("You don't own any private VC!", ephemeral=True)
            return
        for member in vc.members:
            try: await member.move_to(None)
            except: pass
        await vc.delete()
        if vc.id in self.cog.private_channels:
            del self.cog.private_channels[vc.id]
            await self.cog.delete_private_channel(vc.id)
        await interaction.followup.send("Your private VC has been deleted!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)
    
    async def block(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("You don't own any private VC!", ephemeral=True)
            return
        options = []
        for member in interaction.guild.members:
            if (member not in vc.members and not member.bot and member != interaction.user):
                options.append(SelectOption(label=member.name, value=str(member.id)))
        if not options:
            await interaction.response.send_message("No members available to block!", ephemeral=True)
            return
        dropdown = UserSelectDropdown(options, "Select members to block", self.block_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Select members to block:", view=view, ephemeral=True)
    
    async def block_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc: return
        for user_id in selected:
            await self.cog.block_user(vc.id, int(user_id))
        await interaction.followup.send("Selected members blocked from joining!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)


class UserSelectDropdown(ui.Select):
    def __init__(self, options: List[SelectOption], placeholder: str, callback):
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=len(options))
        self.callback_func = callback
    async def callback(self, interaction: discord.Interaction):
        await self.callback_func(interaction, self.values)

class RegionSelectDropdown(ui.Select):
    def __init__(self, options: List[SelectOption], vc: discord.VoiceChannel):
        super().__init__(placeholder="Select a region", options=options)
        self.vc = vc
    async def callback(self, interaction: discord.Interaction):
        region = self.values[0]
        try:
            await self.vc.edit(rtc_region=region if region != "auto" else None)
            await interaction.response.send_message(f"Region set to {self.values[0]}!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to set region: {e}", ephemeral=True)

class VCSelectDropdown(ui.Select):
    def __init__(self, options: List[SelectOption], placeholder: str, callback):
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=1)
        self.callback_func = callback
    async def callback(self, interaction: discord.Interaction):
        await self.callback_func(interaction, self.values)

class SetLimitModal(ui.Modal, title="Set VC User Limit"):
    def __init__(self, vc: discord.VoiceChannel):
        super().__init__()
        self.vc = vc
        self.limit = ui.TextInput(
            label="User Limit (0 for no limit)",
            placeholder="Enter a number between 0 and 99",
            default=str(vc.user_limit) if vc.user_limit else "0",
            max_length=2
        )
        self.add_item(self.limit)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.limit.value)
            if limit < 0 or limit > 99:
                raise ValueError
            await self.vc.edit(user_limit=limit if limit != 0 else None)
            cog = interaction.client.get_cog("JoinToCreate")
            if cog and self.vc.id in cog.private_channels:
                cog.private_channels[self.vc.id]["limit"] = limit
                await cog.save_private_channel(self.vc.id, interaction.guild.id, cog.private_channels[self.vc.id])
            await interaction.response.send_message(f"User limit set to {limit if limit != 0 else 'no limit'}!", ephemeral=True)
            await cog.update_control_panel(interaction.guild)
        except:
            await interaction.response.send_message("Invalid limit! Please enter a number between 0 and 99.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(JoinToCreate(bot))
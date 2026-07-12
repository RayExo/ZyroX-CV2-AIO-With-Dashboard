from fastapi import APIRouter, Depends, HTTPException, Request
from api.dependencies import get_bot, limiter
from api.db_manager import db_manager
from api.schemas import (
    GuildSummary, GuildDetails, PrefixConfig, AutomodConfig, 
    TicketConfig, LevelingConfig, LoggingConfig, TicketEmbed, 
    TicketCategory, LevelingEmbedStyle, PrefixUpdate, 
    AutomodUpdate, LevelingUpdate, LoggingUpdate, TicketUpdate,
    LeaderboardEntry, DiscordChannel, DiscordRole, WelcomeConfig, WelcomeEmbedData, WelcomeUpdate,
    AntiNukeConfig, AntiNukeUpdate, VerificationConfig, VerificationUpdate,
    VanityRoleSetup, AutoRoleConfig, AutoRoleUpdate,
    TrackingConfig, TrackingUpdate, J2CConfig, J2CUpdate, JoinDMConfig, JoinDMUpdate,
    CustomRoleConfig, CustomRoleUpdate, AutoReactConfig, AutoReactUpdate, AutoReactTrigger,
    InvcConfig, InvcUpdate,
    RRConfig, RRUpdate, ReactionRoleEntry,
    InviteStat, InvitesLeaderboard
)
from typing import TYPE_CHECKING, List, Optional
import math
import aiosqlite
import json
import os

if TYPE_CHECKING:
    from core.zyrox import zyrox

router = APIRouter()


@router.get("/", response_model=List[GuildSummary], summary="List all guilds", description="Returns a summary of all guilds the bot is currently in.")
async def list_guilds(bot: "zyrox" = Depends(get_bot)):
    """
    Lists detailed information about all guilds the bot is currently in.
    """
    guilds_list = []
    for guild in bot.guilds:
        guilds_list.append(GuildSummary(
            id=str(guild.id),
            name=guild.name,
            icon_url=str(guild.icon.url) if guild.icon else None,
            owner_id=str(guild.owner_id),
            member_count=guild.member_count or 0
        ))
    return guilds_list

@router.get("/{guild_id}", response_model=GuildDetails, summary="Get guild details", description="Returns detailed metrics and metadata for a specific Discord guild.")
async def get_guild_details(guild_id: int, bot: "zyrox" = Depends(get_bot)):
    """
    Returns detailed info for a specific guild by its ID.
    """
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
        
    return GuildDetails(
        id=str(guild.id),
        name=guild.name,
        icon=str(guild.icon.url) if guild.icon else None,
        owner_id=str(guild.owner_id),
        member_count=guild.member_count or 0,
        role_count=len(guild.roles),
        channel_count=len(guild.channels)
    )

@router.get("/{guild_id}/prefix", response_model=PrefixConfig, summary="Get guild prefix", description="Retrieves the custom command prefix configured for the guild.")
async def get_guild_prefix(guild_id: int):
    """
    Retrieves the custom prefix for a specific guild.
    """
    db = await db_manager.get_connection('db/prefix.db')
    cursor = await db.execute("SELECT prefix FROM prefixes WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    prefix = row[0] if row else ">"
    return PrefixConfig(guild_id=guild_id, prefix=prefix)

@router.post("/{guild_id}/prefix", summary="Update guild prefix", description="Updates or resets the custom command prefix for the specified guild.")
async def update_guild_prefix(guild_id: int, data: PrefixUpdate):
    """
    Updates the custom prefix for a specific guild.
    """
    if not data.prefix or len(data.prefix) > 10:
        raise HTTPException(status_code=400, detail="Invalid prefix. Must be 1-10 characters.")

    db = await db_manager.get_connection('db/prefix.db')
    await db.execute(
        "INSERT OR REPLACE INTO prefixes (guild_id, prefix) VALUES (?, ?)",
        (guild_id, data.prefix)
    )
    await db.commit()
    
    return {"status": "success", "guild_id": guild_id, "new_prefix": data.prefix}



@router.get("/{guild_id}/automod", response_model=AutomodConfig, summary="Get AutoMod config", description="Retrieves active AutoMod rules, punishments, and ignored entities.")
async def get_guild_automod(guild_id: int):
    """
    Retrieves the AutoMod configuration for a specific guild.
    """
    db = await db_manager.get_connection('db/automod.db')
    # Check enabled status
    cursor = await db.execute("SELECT enabled FROM automod WHERE guild_id = ?", (guild_id,))
    enabled_row = await cursor.fetchone()
    enabled = bool(enabled_row[0]) if enabled_row else False

    # Get punishments
    cursor = await db.execute("SELECT event, punishment FROM automod_punishments WHERE guild_id = ?", (guild_id,))
    punishments = {row[0]: row[1] for row in await cursor.fetchall()}

    # Get ignored items
    cursor = await db.execute("SELECT type, id FROM automod_ignored WHERE guild_id = ?", (guild_id,))
    ignored_items = await cursor.fetchall()
    ignored_roles = [row[1] for row in ignored_items if row[0] == 'role']
    ignored_channels = [row[1] for row in ignored_items if row[0] == 'channel']

    # Get logging channel
    cursor = await db.execute("SELECT log_channel FROM automod_logging WHERE guild_id = ?", (guild_id,))
    logging_row = await cursor.fetchone()
    logging_channel = logging_row[0] if logging_row else None

    return AutomodConfig(
        guild_id=guild_id,
        enabled=enabled,
        punishments=punishments,
        ignored_roles=ignored_roles,
        ignored_channels=ignored_channels,
        logging_channel=logging_channel
    )

@router.patch("/{guild_id}/automod", summary="Update AutoMod config", description="Partially updates the AutoMod configuration components.")
async def patch_guild_automod(guild_id: int, data: AutomodUpdate):
    """
    Updates parts of the AutoMod configuration for a specific guild.
    """
    db = await db_manager.get_connection('db/automod.db')
    if data.enabled is not None:
        await db.execute(
            "INSERT OR REPLACE INTO automod (guild_id, enabled) VALUES (?, ?)",
            (guild_id, 1 if data.enabled else 0)
        )

    if data.punishments is not None:
        for event, punishment in data.punishments.items():
            await db.execute(
                "INSERT OR REPLACE INTO automod_punishments (guild_id, event, punishment) VALUES (?, ?, ?)",
                (guild_id, event, punishment)
            )

    if data.ignored_roles is not None:
        await db.execute("DELETE FROM automod_ignored WHERE guild_id = ? AND type = 'role'", (guild_id,))
        for role_id in data.ignored_roles:
            await db.execute(
                "INSERT OR REPLACE INTO automod_ignored (guild_id, type, id) VALUES (?, 'role', ?)",
                (guild_id, role_id)
            )

    if data.ignored_channels is not None:
        await db.execute("DELETE FROM automod_ignored WHERE guild_id = ? AND type = 'channel'", (guild_id,))
        for channel_id in data.ignored_channels:
            await db.execute(
                "INSERT OR REPLACE INTO automod_ignored (guild_id, type, id) VALUES (?, 'channel', ?)",
                (guild_id, channel_id)
            )

    if data.logging_channel is not None:
        await db.execute(
            "INSERT OR REPLACE INTO automod_logging (guild_id, log_channel) VALUES (?, ?)",
            (guild_id, data.logging_channel)
        )

    await db.commit()
    
    return {"status": "success", "guild_id": guild_id}

@router.get("/{guild_id}/tickets", response_model=TicketConfig, summary="Get Ticket config", description="Retrieves the support ticket system setup, categories, and staff roles.")
async def get_guild_tickets(guild_id: int):
    """
    Retrieves the ticket system configuration for a specific guild.
    """
    db = await db_manager.get_connection('db/ticket.db')
    
    # Get basic config
    cursor = await db.execute(
        "SELECT panel_channel_id, panel_message_id, logging_channel_id, panel_type, embed_title, embed_description, embed_color, embed_image_url, embed_thumbnail_url, closed_category_id FROM guild_configs WHERE guild_id = ?", 
        (guild_id,)
    )
    config_row = await cursor.fetchone()
    
    # Get categories and identify staff roles
    cursor = await db.execute(
        "SELECT name, emoji, notified_roles, button_style, discord_category_id FROM ticket_categories WHERE guild_id = ?", 
        (guild_id,)
    )
    categories_rows = await cursor.fetchall()
    categories = []
    staff_roles = set()
    for row in categories_rows:
        if row["notified_roles"]:
            roles = [int(r.strip()) for r in row["notified_roles"].split(",") if r.strip()]
            category_roles = roles
            for r in roles:
                staff_roles.add(r)
        else:
            category_roles = []

        categories.append(TicketCategory(
            name=row["name"],
            emoji=row["emoji"],
            staff_roles=category_roles,
            button_style=row["button_style"],
            discord_category_id=row["discord_category_id"]
        ))

    # Get open ticket count
    cursor = await db.execute(
        "SELECT COUNT(*) FROM open_tickets WHERE guild_id = ?", 
        (guild_id,)
    )
    count_row = await cursor.fetchone()
    open_ticket_count = count_row[0] if count_row else 0

    return TicketConfig(
        guild_id=guild_id,
        panel_channel=config_row["panel_channel_id"] if config_row else None,
        panel_message=config_row["panel_message_id"] if config_row else None,
        logging_channel=config_row["logging_channel_id"] if config_row else None,
        closed_category=config_row["closed_category_id"] if config_row else None,
        panel_type=config_row["panel_type"] if config_row else "button",
        embed=TicketEmbed(
            title=config_row["embed_title"] if config_row else "Support Department",
            description=config_row["embed_description"] if config_row else "Open a ticket below to talk to our staff.",
            color=config_row["embed_color"] if config_row else None,
            image_url=config_row["embed_image_url"] if config_row else None,
            thumbnail_url=config_row["embed_thumbnail_url"] if config_row else None
        ),
        categories=categories,
        staff_roles=list(staff_roles),
        open_ticket_count=open_ticket_count
    )

@router.patch("/{guild_id}/tickets", summary="Update Ticket config", description="Updates the ticket system configuration, including categories and embed details.")
async def patch_guild_tickets(guild_id: int, data: TicketUpdate):
    """
    Updates the ticket system configuration for a specific guild.
    """
    db = await db_manager.get_connection('db/ticket.db')
    
    # Initialize config row if not exists
    cursor = await db.execute("SELECT guild_id FROM guild_configs WHERE guild_id = ?", (guild_id,))
    if not await cursor.fetchone():
        await db.execute("INSERT INTO guild_configs (guild_id) VALUES (?)", (guild_id,))

    if data.panel_channel is not None:
        await db.execute("UPDATE guild_configs SET panel_channel_id = ? WHERE guild_id = ?", (data.panel_channel, guild_id))
    
    if data.logging_channel is not None:
        await db.execute("UPDATE guild_configs SET logging_channel_id = ? WHERE guild_id = ?", (data.logging_channel, guild_id))
        
    if data.closed_category is not None:
        await db.execute("UPDATE guild_configs SET closed_category_id = ? WHERE guild_id = ?", (data.closed_category, guild_id))

    if data.panel_type is not None:
        await db.execute("UPDATE guild_configs SET panel_type = ? WHERE guild_id = ?", (data.panel_type, guild_id))
        
    if data.embed_title is not None:
        await db.execute("UPDATE guild_configs SET embed_title = ? WHERE guild_id = ?", (data.embed_title, guild_id))

    if data.embed_description is not None:
        await db.execute("UPDATE guild_configs SET embed_description = ? WHERE guild_id = ?", (data.embed_description, guild_id))

    if data.embed_color is not None:
        await db.execute("UPDATE guild_configs SET embed_color = ? WHERE guild_id = ?", (data.embed_color, guild_id))

    if data.embed_image_url is not None:
        await db.execute("UPDATE guild_configs SET embed_image_url = ? WHERE guild_id = ?", (data.embed_image_url, guild_id))

    if data.embed_thumbnail_url is not None:
        await db.execute("UPDATE guild_configs SET embed_thumbnail_url = ? WHERE guild_id = ?", (data.embed_thumbnail_url, guild_id))

    if data.staff_roles is not None:
        roles_str = ",".join(map(str, data.staff_roles))
        await db.execute("UPDATE guild_configs SET staff_roles = ? WHERE guild_id = ?", (roles_str, guild_id))

    if data.categories is not None:
        # Clear existing categories
        await db.execute("DELETE FROM ticket_categories WHERE guild_id = ?", (guild_id,))
        for cat in data.categories:
            roles_str = ",".join(map(str, cat.staff_roles))
            await db.execute(
                "INSERT INTO ticket_categories (guild_id, name, emoji, notified_roles, button_style, discord_category_id) VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, cat.name, cat.emoji, roles_str, cat.button_style, cat.discord_category_id)
            )

    await db.commit()
    return {"status": "success", "guild_id": guild_id}
    return {"status": "success", "guild_id": guild_id}



@router.get("/{guild_id}/leveling", response_model=LevelingConfig, summary="Get Leveling config", description="Retrieves experience points settings, cooldowns, and rank card styles.")
async def get_guild_leveling(guild_id: int):
    """
    Retrieves the leveling system configuration for a specific guild.
    """
    db = await db_manager.get_connection('db/leveling.db')
    cursor = await db.execute("SELECT * FROM leveling_settings WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    
    if not row:
        return LevelingConfig(
            guild_id=guild_id,
            enabled=False,
            xp_per_message=20,
            cooldown=60,
            level_up_channel=None,
            embed_style=LevelingEmbedStyle(color="#000000")
        )

    embed_color = row["embed_color"] if row["embed_color"] is not None else 0
    color_hex = f"#{embed_color:06x}"

    return LevelingConfig(
        guild_id=guild_id,
        enabled=bool(row["enabled"]),
        xp_per_message=row["xp_per_message"],
        cooldown=row["cooldown_seconds"],
        level_up_channel=row["channel_id"],
        embed_style=LevelingEmbedStyle(
            color=color_hex,
            thumbnail=bool(row["thumbnail_enabled"]),
            image=row["level_image"]
        )
    )

@router.patch("/{guild_id}/leveling", summary="Update Leveling config", description="Modifies the leveling system settings including XP rates and channel notifications.")
async def patch_guild_leveling(guild_id: int, data: LevelingUpdate):
    """
    Updates parts of the leveling configuration for a specific guild.
    """
    db = await db_manager.get_connection('db/leveling.db')
    # We use a series of updates or a single dynamic update.
    # For simplicity and robustness with INSERT OR REPLACE:
    
    cursor = await db.execute("SELECT * FROM leveling_settings WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    
    if not row:
        # Create default entry first if it doesn't exist
        await db.execute("INSERT INTO leveling_settings (guild_id) VALUES (?)", (guild_id,))
        await db.commit()

    if data.enabled is not None:
        await db.execute("UPDATE leveling_settings SET enabled = ? WHERE guild_id = ?", (1 if data.enabled else 0, guild_id))
    
    if data.xp_per_message is not None:
        await db.execute("UPDATE leveling_settings SET xp_per_message = ? WHERE guild_id = ?", (data.xp_per_message, guild_id))
        
    if data.cooldown is not None:
        await db.execute("UPDATE leveling_settings SET cooldown_seconds = ? WHERE guild_id = ?", (data.cooldown, guild_id))
        
    if data.level_up_channel is not None:
        await db.execute("UPDATE leveling_settings SET channel_id = ? WHERE guild_id = ?", (data.level_up_channel, guild_id))
        
    if data.embed_color is not None:
        try:
            # Convert hex to int
            clean_hex = data.embed_color.lstrip('#')
            color_int = int(clean_hex, 16)
            await db.execute("UPDATE leveling_settings SET embed_color = ? WHERE guild_id = ?", (color_int, guild_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid hex color format.")

    await db.commit()
    
    return {"status": "success", "guild_id": guild_id}


@router.get("/{guild_id}/welcome", response_model=WelcomeConfig, summary="Get Welcome config", description="Retrieves the greet/welcome messages setup.")
async def get_guild_welcome(guild_id: int):
    import aiosqlite
    import json
    
    async with aiosqlite.connect("db/welcome.db") as db:
        async with db.execute("SELECT welcome_type, welcome_message, channel_id, embed_data, auto_delete_duration FROM welcome WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            
    if not row:
        return WelcomeConfig(
            guild_id=guild_id,
        )
        
    welcome_type, welcome_message, channel_id, embed_data, auto_delete_duration = row
    
    embed_parsed = None
    if embed_data:
        try:
            embed_parsed = WelcomeEmbedData(**json.loads(embed_data))
        except:
            pass
            
    return WelcomeConfig(
        guild_id=guild_id,
        welcome_type=welcome_type,
        welcome_message=welcome_message,
        channel_id=channel_id,
        embed_data=embed_parsed,
        auto_delete_duration=auto_delete_duration
    )

@router.patch("/{guild_id}/welcome", summary="Update Welcome config", description="Updates welcome/greet configuration.")
async def patch_guild_welcome(guild_id: int, data: WelcomeUpdate):
    import aiosqlite
    import json
    
    async with aiosqlite.connect("db/welcome.db") as db:
        # Get existing or create
        async with db.execute("SELECT welcome_type, welcome_message, channel_id, embed_data, auto_delete_duration FROM welcome WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            
        if not row:
            await db.execute(
                "INSERT INTO welcome (guild_id, welcome_type, welcome_message, channel_id, embed_data, auto_delete_duration) VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, data.welcome_type or "simple", data.welcome_message, data.channel_id, json.dumps(data.embed_data.dict()) if data.embed_data else None, data.auto_delete_duration)
            )
        else:
            wt, wm, chid, ed, auth_del = row
            
            new_wt = data.welcome_type if data.welcome_type is not None else wt
            new_wm = data.welcome_message if data.welcome_message is not None else wm
            new_chid = data.channel_id if data.channel_id is not None else chid
            new_auth_del = data.auto_delete_duration if data.auto_delete_duration is not None else auth_del
            
            new_ed = ed
            if data.embed_data is not None:
                new_ed = json.dumps(data.embed_data.dict())
                
            await db.execute(
                "UPDATE welcome SET welcome_type = ?, welcome_message = ?, channel_id = ?, embed_data = ?, auto_delete_duration = ? WHERE guild_id = ?",
                (new_wt, new_wm, new_chid, new_ed, new_auth_del, guild_id)
            )
            
        await db.commit()
        
    return {"status": "success", "guild_id": guild_id}


@router.get("/{guild_id}/antinuke", response_model=AntiNukeConfig, summary="Get AntiNuke config")
async def get_guild_antinuke(guild_id: int):
    import aiosqlite
    
    async with aiosqlite.connect("db/anti.db") as db:
        async with db.execute("SELECT status FROM antinuke WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
        
        whitelisted = []
        # Need to check if table exists first since it's created by the cog
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='whitelisted_users'")
        if await cursor.fetchone():
            async with db.execute("SELECT user_id FROM whitelisted_users WHERE guild_id = ?", (guild_id,)) as wl_cursor:
                wl_rows = await wl_cursor.fetchall()
                whitelisted = [str(r[0]) for r in wl_rows]
            
    return AntiNukeConfig(
        guild_id=guild_id,
        status=bool(row[0]) if row else False,
        whitelisted_users=whitelisted
    )

@router.patch("/{guild_id}/antinuke", summary="Update AntiNuke config")
async def patch_guild_antinuke(guild_id: int, data: AntiNukeUpdate):
    import aiosqlite
    
    async with aiosqlite.connect("db/anti.db") as db:
        if data.status is not None:
            # Get existing or create
            async with db.execute("SELECT status FROM antinuke WHERE guild_id = ?", (guild_id,)) as cursor:
                row = await cursor.fetchone()
                
            if not row:
                await db.execute(
                    "INSERT INTO antinuke (guild_id, status) VALUES (?, ?)",
                    (guild_id, data.status)
                )
            else:
                await db.execute(
                    "UPDATE antinuke SET status = ? WHERE guild_id = ?",
                    (data.status, guild_id)
                )
        
        if data.add_whitelist:
            # Only add if table exists to avoid errors
            cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='whitelisted_users'")
            if await cursor.fetchone():
                try:
                    user_id = int(data.add_whitelist)
                    # Check if already whitelisted
                    async with db.execute("SELECT * FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)) as wl_cursor:
                        if not await wl_cursor.fetchone():
                            await db.execute("INSERT INTO whitelisted_users (guild_id, user_id, ban, kick, prune, botadd, serverup, memup, chcr, chdl, chup, rlcr, rlup, rldl, meneve, mngweb, mngstemo) VALUES (?, ?, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True)", (guild_id, user_id))
                except ValueError:
                    pass
                    
        if data.remove_whitelist:
            cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='whitelisted_users'")
            if await cursor.fetchone():
                try:
                    user_id = int(data.remove_whitelist)
                    await db.execute("DELETE FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
                except ValueError:
                    pass
            
        await db.commit()
        
    return {"status": "success", "guild_id": guild_id}


@router.get("/{guild_id}/verification", response_model=VerificationConfig, summary="Get Verification config")
async def get_guild_verification(guild_id: int):
    import aiosqlite
    
    async with aiosqlite.connect("db/verification.db") as db:
        async with db.execute("SELECT verification_channel_id, verified_role_id, log_channel_id, verification_method, enabled FROM verification_config WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            
    if row:
        return VerificationConfig(
            guild_id=guild_id,
            verification_channel_id=row[0],
            verified_role_id=row[1],
            log_channel_id=row[2],
            verification_method=row[3],
            enabled=bool(row[4])
        )
    return VerificationConfig(
        guild_id=guild_id,
        verification_channel_id=None,
        verified_role_id=None,
        log_channel_id=None,
        verification_method="both",
        enabled=True
    )

@router.patch("/{guild_id}/verification", summary="Update Verification config")
async def patch_guild_verification(guild_id: int, data: VerificationUpdate):
    import aiosqlite
    
    async with aiosqlite.connect("db/verification.db") as db:
        async with db.execute("SELECT * FROM verification_config WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            
        if not row:
            await db.execute(
                "INSERT INTO verification_config (guild_id, verification_channel_id, verified_role_id, log_channel_id, verification_method, enabled) VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, data.verification_channel_id or 0, data.verified_role_id or 0, data.log_channel_id or 0, data.verification_method or "both", data.enabled if data.enabled is not None else True)
            )
        else:
            await db.execute(
                "UPDATE verification_config SET verification_channel_id = COALESCE(?, verification_channel_id), verified_role_id = COALESCE(?, verified_role_id), log_channel_id = COALESCE(?, log_channel_id), verification_method = COALESCE(?, verification_method), enabled = COALESCE(?, enabled) WHERE guild_id = ?",
                (data.verification_channel_id, data.verified_role_id, data.log_channel_id, data.verification_method, data.enabled, guild_id)
            )
            
        await db.commit()
        
    return {"status": "success", "guild_id": guild_id}


@router.get("/{guild_id}/vanityroles", response_model=List[VanityRoleSetup], summary="Get Vanity Roles setups")
async def get_guild_vanityroles(guild_id: int):
    import aiosqlite
    
    setups = []
    async with aiosqlite.connect("db/vanity.db") as db:
        async with db.execute("SELECT vanity, role_id, log_channel_id FROM vanity_roles WHERE guild_id = ?", (guild_id,)) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                setups.append(VanityRoleSetup(
                    vanity=row[0],
                    role_id=row[1],
                    log_channel_id=row[2]
                ))
    return setups

@router.post("/{guild_id}/vanityroles", summary="Add/Update a Vanity Role setup")
async def post_guild_vanityroles(guild_id: int, data: VanityRoleSetup):
    import aiosqlite
    
    async with aiosqlite.connect("db/vanity.db") as db:
        await db.execute(
            "INSERT OR REPLACE INTO vanity_roles (guild_id, vanity, role_id, log_channel_id, current_status) VALUES (?, ?, ?, ?, NULL)",
            (guild_id, data.vanity.lower(), data.role_id, data.log_channel_id)
        )
        await db.commit()
        
    return {"status": "success", "vanity": data.vanity}

@router.delete("/{guild_id}/vanityroles/{vanity}", summary="Delete a Vanity Role setup")
async def delete_guild_vanityroles(guild_id: int, vanity: str):
    import aiosqlite
    
    async with aiosqlite.connect("db/vanity.db") as db:
        await db.execute("DELETE FROM vanity_roles WHERE guild_id = ? AND vanity = ?", (guild_id, vanity.lower()))
        await db.commit()
        
    return {"status": "success"}


@router.get("/{guild_id}/autorole", response_model=AutoRoleConfig, summary="Get AutoRole config")
async def get_guild_autorole(guild_id: int):
    import aiosqlite
    
    async with aiosqlite.connect("db/autorole.db") as db:
        # Ensure table exists
        await db.execute("""
            CREATE TABLE IF NOT EXISTS autorole (
                guild_id INTEGER PRIMARY KEY,
                bots TEXT NOT NULL DEFAULT '[]',
                humans TEXT NOT NULL DEFAULT '[]'
            )
        """)
        await db.commit()
        
        async with db.execute("SELECT bots, humans FROM autorole WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            
    if row:
        bots_str, humans_str = row
        try:
            bots = [r.strip() for r in bots_str.replace('[','').replace(']','').split(',') if r.strip()]
        except Exception:
            bots = []
            
        try:
            humans = [r.strip() for r in humans_str.replace('[','').replace(']','').split(',') if r.strip()]
        except Exception:
            humans = []
            
        return AutoRoleConfig(guild_id=str(guild_id), bots=bots, humans=humans)
        
    return AutoRoleConfig(guild_id=str(guild_id), bots=[], humans=[])

@router.patch("/{guild_id}/autorole", summary="Update AutoRole config")
async def patch_guild_autorole(guild_id: int, data: AutoRoleUpdate):
    import aiosqlite
    
    async with aiosqlite.connect("db/autorole.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS autorole (
                guild_id INTEGER PRIMARY KEY,
                bots TEXT NOT NULL DEFAULT '[]',
                humans TEXT NOT NULL DEFAULT '[]'
            )
        """)
        
        # Build the bracket-format strings the bot cog expects
        if data.bots is not None:
            bots_str = str([int(b) for b in data.bots if b and b.isdigit()])
        else:
            # Get existing to keep
            async with db.execute("SELECT bots FROM autorole WHERE guild_id = ?", (guild_id,)) as cursor:
                old = await cursor.fetchone()
            bots_str = old[0] if old else '[]'
            
        if data.humans is not None:
            humans_str = str([int(h) for h in data.humans if h and h.isdigit()])
        else:
            async with db.execute("SELECT humans FROM autorole WHERE guild_id = ?", (guild_id,)) as cursor:
                old = await cursor.fetchone()
            humans_str = old[0] if old else '[]'
            
        await db.execute(
            "INSERT OR REPLACE INTO autorole (guild_id, bots, humans) VALUES (?, ?, ?)",
            (guild_id, bots_str, humans_str)
        )
        await db.commit()
        
    return {"status": "success"}


@router.get("/{guild_id}/welcome", response_model=WelcomeConfig, summary="Get Welcome config")
async def get_guild_welcome(guild_id: int):
    import aiosqlite
    import json
    
    async with aiosqlite.connect("db/welcome.db") as db:
        async with db.execute("SELECT welcome_type, welcome_message, channel_id, embed_data, auto_delete_duration FROM welcome WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            
    if row:
        w_type, w_msg, channel_id, embed_data_str, auto_del = row
        edata = None
        if embed_data_str:
            try:
                edata_dict = json.loads(embed_data_str)
                edata = WelcomeEmbedData(**edata_dict)
            except:
                pass
        return WelcomeConfig(
            guild_id=guild_id,
            welcome_type=w_type,
            welcome_message=w_msg,
            channel_id=channel_id,
            embed_data=edata,
            auto_delete_duration=auto_del
        )
        
    return WelcomeConfig(guild_id=guild_id)

@router.patch("/{guild_id}/welcome", summary="Update Welcome config")
async def patch_guild_welcome(guild_id: int, data: WelcomeUpdate):
    import aiosqlite
    import json
    
    async with aiosqlite.connect("db/welcome.db") as db:
        async with db.execute("SELECT welcome_type, welcome_message, channel_id, embed_data, auto_delete_duration FROM welcome WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            
        current_type = row[0] if row else None
        current_msg = row[1] if row else None
        current_channel = row[2] if row else None
        current_embed_str = row[3] if row else None
        current_auto = row[4] if row else None
        
        new_type = data.welcome_type if data.welcome_type is not None else current_type
        new_msg = data.welcome_message if data.welcome_message is not None else current_msg
        new_channel = data.channel_id if data.channel_id is not None else current_channel
        new_auto = data.auto_delete_duration if data.auto_delete_duration is not None else current_auto
        
        new_embed_str = current_embed_str
        if data.embed_data is not None:
            new_embed_str = data.embed_data.json(exclude_none=True)
            
        if not row:
            await db.execute(
                "INSERT INTO welcome (guild_id, welcome_type, welcome_message, channel_id, embed_data, auto_delete_duration) VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, new_type, new_msg, new_channel, new_embed_str, new_auto)
            )
        else:
            await db.execute(
                "UPDATE welcome SET welcome_type=?, welcome_message=?, channel_id=?, embed_data=?, auto_delete_duration=? WHERE guild_id=?",
                (new_type, new_msg, new_channel, new_embed_str, new_auto, guild_id)
            )
            
        await db.commit()
    return {"status": "success", "guild_id": guild_id}

@router.delete("/{guild_id}/welcome", summary="Delete Welcome config")
async def delete_guild_welcome(guild_id: int):
    import aiosqlite
    async with aiosqlite.connect("db/welcome.db") as db:
        await db.execute("DELETE FROM welcome WHERE guild_id = ?", (guild_id,))
        await db.commit()
    return {"status": "success"}


@router.get("/{guild_id}/tracking", response_model=TrackingConfig, summary="Get Tracking config")
async def get_guild_tracking(guild_id: int):
    import aiosqlite
    async with aiosqlite.connect("db/invite.db") as db:
        async with db.execute("SELECT channel_id FROM logging WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
    return TrackingConfig(guild_id=guild_id, channel_id=row[0] if row else None)

@router.patch("/{guild_id}/tracking", summary="Update Tracking config")
async def patch_guild_tracking(guild_id: int, data: TrackingUpdate):
    import aiosqlite
    async with aiosqlite.connect("db/invite.db") as db:
        await db.execute("INSERT OR REPLACE INTO logging (guild_id, channel_id) VALUES (?, ?)", (guild_id, data.channel_id))
        await db.commit()
    return {"status": "success"}

@router.get("/{guild_id}/j2c", response_model=J2CConfig, summary="Get J2C config")
async def get_guild_j2c(guild_id: int):
    import aiosqlite
    async with aiosqlite.connect("j2c_data.db") as db:
        # Ensure table exists
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
        await db.commit()
        
        async with db.execute("SELECT join_channel_id, control_channel_id, category_id FROM guild_setup WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
    if row:
        return J2CConfig(
            guild_id=str(guild_id), 
            join_channel_id=str(row[0]) if row[0] else None, 
            control_channel_id=str(row[1]) if row[1] else None,
            category_id=str(row[2]) if row[2] else None
        )
    return J2CConfig(guild_id=str(guild_id))

@router.patch("/{guild_id}/j2c", summary="Update J2C config")
async def patch_guild_j2c(guild_id: int, data: J2CUpdate, bot: "zyrox" = Depends(get_bot)):
    import aiosqlite
    
    def to_id(val):
        if not val or val == "none": return None
        try: return int(val)
        except: return None

    join_ch = to_id(data.join_channel_id)
    ctrl_ch = to_id(data.control_channel_id)
    cat_ch = to_id(data.category_id)
    
    async with aiosqlite.connect("j2c_data.db") as db:
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
        
        async with db.execute("SELECT control_message_id FROM guild_setup WHERE guild_id = ?", (guild_id,)) as cursor:
            existing = await cursor.fetchone()
        
        ctrl_msg_id = existing[0] if existing else None
        
        await db.execute(
            "INSERT OR REPLACE INTO guild_setup (guild_id, join_channel_id, control_channel_id, control_message_id, category_id) VALUES (?, ?, ?, ?, ?)", 
            (guild_id, join_ch, ctrl_ch, ctrl_msg_id, cat_ch)
        )
        await db.commit()

    # Update cog memory cache and send/update the control panel in real-time
    cog = bot.get_cog("JoinToCreate")
    if cog:
        if not join_ch or not ctrl_ch:
            if guild_id in cog.setup_data:
                del cog.setup_data[guild_id]
        else:
            cog.setup_data[guild_id] = {
                "join_channel_id": join_ch,
                "control_channel_id": ctrl_ch,
                "control_message_id": ctrl_msg_id,
                "category_id": cat_ch
            }
            guild = bot.get_guild(guild_id)
            if guild:
                async def update_or_send_panel():
                    try:
                        control_channel = guild.get_channel(ctrl_ch)
                        if control_channel:
                            msg = None
                            if ctrl_msg_id:
                                try:
                                    msg = await control_channel.fetch_message(ctrl_msg_id)
                                except:
                                    pass
                            
                            from cogs.commands.j2c import ControlPanelView
                            if msg:
                                view = ControlPanelView(cog, guild)
                                await msg.edit(view=view, embed=None, content=None)
                            else:
                                view = ControlPanelView(cog, guild)
                                msg = await control_channel.send(view=view)
                                cog.setup_data[guild_id]["control_message_id"] = msg.id
                                await cog.save_guild_setup(guild_id, cog.setup_data[guild_id])
                    except Exception as e:
                        print(f"Error updating/sending control panel via API: {e}")

                bot.loop.create_task(update_or_send_panel())

    return {"status": "success"}


@router.get("/{guild_id}/joindm", response_model=JoinDMConfig, summary="Get JoinDM config")
async def get_guild_joindm(guild_id: int):
    config_file = 'jsondb/joindm_messages.json'
    os.makedirs('jsondb', exist_ok=True)
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    data = {}
                else:
                    data = json.loads(content)
                    if not isinstance(data, dict):
                        data = {}
        except (json.JSONDecodeError, Exception):
            data = {}
            
        return JoinDMConfig(guild_id=str(guild_id), message=data.get(str(guild_id)))
    
    return JoinDMConfig(guild_id=str(guild_id))

@router.patch("/{guild_id}/joindm", summary="Update JoinDM config")
async def patch_guild_joindm(guild_id: int, data: JoinDMUpdate):
    config_file = 'jsondb/joindm_messages.json'
    os.makedirs('jsondb', exist_ok=True)
    
    messages = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                content = f.read().strip()
                if content:
                    messages = json.loads(content)
                    if not isinstance(messages, dict):
                        messages = {}
        except (json.JSONDecodeError, Exception):
            messages = {}

    messages[str(guild_id)] = data.message
    
    with open(config_file, 'w') as f:
        json.dump(messages, f, indent=2)
        
    return {"status": "success"}

@router.get("/{guild_id}/customroles", response_model=CustomRoleConfig, summary="Get CustomRoles config")
async def get_guild_customroles(guild_id: int):
    import aiosqlite
    async with aiosqlite.connect('db/customrole.db') as db:
        async with db.execute("SELECT staff, girl, vip, guest, frnd, reqrole FROM roles WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
    if row:
        return CustomRoleConfig(
            guild_id=str(guild_id),
            staff=str(row[0]) if row[0] else None,
            girl=str(row[1]) if row[1] else None,
            vip=str(row[2]) if row[2] else None,
            guest=str(row[3]) if row[3] else None,
            frnd=str(row[4]) if row[4] else None,
            reqrole=str(row[5]) if row[5] else None
        )
    return CustomRoleConfig(guild_id=str(guild_id))

@router.patch("/{guild_id}/customroles", summary="Update CustomRoles config")
async def patch_guild_customroles(guild_id: int, data: CustomRoleUpdate):
    import aiosqlite
    
    # Convert string IDs to ints for DB INTEGER columns
    def to_int(val):
        if val is None: return None
        try: return int(val)
        except: return None
    
    async with aiosqlite.connect('db/customrole.db') as db:
        async with db.execute("SELECT * FROM roles WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
        
        if not row:
            await db.execute(
                "INSERT INTO roles (guild_id, staff, girl, vip, guest, frnd, reqrole) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (guild_id, to_int(data.staff), to_int(data.girl), to_int(data.vip), to_int(data.guest), to_int(data.frnd), to_int(data.reqrole))
            )
        else:
            # We have a row, update only provided fields
            update_fields = []
            params = []
            for field, value in data.dict(exclude_unset=True).items():
                update_fields.append(f"{field} = ?")
                params.append(to_int(value))
            
            if update_fields:
                query = f"UPDATE roles SET {', '.join(update_fields)} WHERE guild_id = ?"
                params.append(guild_id)
                await db.execute(query, params)
        await db.commit()
    return {"status": "success"}

@router.get("/{guild_id}/logging", response_model=LoggingConfig, summary="Get Logging config", description="Retrieves the event logging configuration and designated log channels.")
async def get_guild_logging(guild_id: int, bot: "zyrox" = Depends(get_bot)):
    """
    Retrieves the logging configuration for a specific guild.
    """
    cog = bot.get_cog("Logging")
    config = None
    
    if cog and guild_id in cog.config_cache:
        config = cog.config_cache[guild_id]
    else:
        # Try reading from file as fallback
        import json
        import os
        config_file = "jsondb/logging_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    data = json.load(f)
                    config = data.get(str(guild_id))
            except:
                pass

    if not config:
        return LoggingConfig(
            guild_id=guild_id,
            log_enabled={},
            log_channels={},
            ignore_channels=[],
            ignore_roles=[],
            ignore_users=[],
            auto_delete_duration=None
        )

    return LoggingConfig(
        guild_id=guild_id,
        log_enabled=config.get("log_enabled", {}),
        log_channels=config.get("log_channels", {}),
        ignore_channels=config.get("ignore_channels", []),
        ignore_roles=config.get("ignore_roles", []),
        ignore_users=config.get("ignore_users", []),
        auto_delete_duration=config.get("auto_delete_duration")
    )

@router.patch("/{guild_id}/logging", summary="Update Logging config", description="Updates which Discord events are logged and where they are posted.")
async def patch_guild_logging(guild_id: int, data: LoggingUpdate, bot: "zyrox" = Depends(get_bot)):
    """
    Updates the logging configuration for a specific guild.
    """
    cog = bot.get_cog("Logging")
    if not cog:
        raise HTTPException(status_code=503, detail="Logging service is currently unavailable.")

    # Get current config or defaults
    current_config = cog.config_cache.get(guild_id, {})
    
    log_channels = current_config.get("log_channels", {})
    if data.log_channels is not None:
        log_channels.update(data.log_channels)
        
    log_enabled = current_config.get("log_enabled", {})
    if data.log_enabled is not None:
        log_enabled.update(data.log_enabled)

    await cog._save_log_config(
        guild_id,
        log_channels,
        log_enabled,
        current_config.get("ignore_channels", []),
        current_config.get("ignore_roles", []),
        current_config.get("ignore_users", []),
        current_config.get("auto_delete_duration")
    )
    
    return {"status": "success", "guild_id": guild_id}

@router.get("/{guild_id}/leveling/leaderboard", response_model=List[LeaderboardEntry], summary="Get leveling leaderboard", description="Returns top users by XP for a specific guild.")
async def get_leveling_leaderboard(guild_id: int, bot: "zyrox" = Depends(get_bot)):
    db = await db_manager.get_connection('db/leveling.db')
    cursor = await db.execute(
        "SELECT user_id, xp FROM user_xp WHERE guild_id = ? ORDER BY xp DESC LIMIT 100", 
        (guild_id,)
    )
    rows = await cursor.fetchall()
    
    leaderboard = []
    guild = bot.get_guild(guild_id)
    
    for row in rows:
        user_id = row["user_id"]
        xp = row["xp"]
        # Calculate level: sqrt(xp/100)
        level = int(math.sqrt(xp / 100)) if xp >= 0 else 0
        
        # Try to get member name
        name = f"User {user_id}"
        if guild:
            member = guild.get_member(user_id)
            if member:
                name = member.display_name
            else:
                try:
                    user = await bot.fetch_user(user_id)
                    name = user.name
                except:
                    pass
        
        leaderboard.append(LeaderboardEntry(
            user_id=str(user_id),
            name=name,
            level=level,
            xp=xp
        ))
    
    return leaderboard

@router.get("/{guild_id}/channels", response_model=List[DiscordChannel], summary="Get guild channels", description="Returns a list of all channels for the specific guild.")
async def get_guild_channels(guild_id: int, bot: "zyrox" = Depends(get_bot)):
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
        
    channels = []
    for canal in guild.channels:
        try:
            # Handle both discord.ChannelType enum and literal ints
            c_type = canal.type.value if hasattr(canal.type, 'value') else int(canal.type)
            channels.append(DiscordChannel(
                id=str(canal.id),
                name=canal.name,
                type=str(c_type)
            ))
        except:
            continue
    return channels

@router.get("/{guild_id}/roles", response_model=List[DiscordRole], summary="Get guild roles", description="Returns a list of roles for the specific guild.")
async def get_guild_roles(guild_id: int, bot: "zyrox" = Depends(get_bot)):
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
        
    roles = []
    for role in guild.roles:
        # Avoid @everyone role if desired, but frontend might need filtering. Let's return all.
        roles.append(DiscordRole(
            id=str(role.id),
            name=role.name,
            color=role.color.value,
            position=role.position
        ))
    # Sort roles by position descending
    roles.sort(key=lambda x: x.position, reverse=True)
    return roles


# ========== INVC ROLE (Voice Role) ==========



# ========== AUTO REACT ==========

@router.get("/{guild_id}/autoreact", response_model=AutoReactConfig, summary="Get AutoReact config")
async def get_guild_autoreact(guild_id: int):
    import aiosqlite
    async with aiosqlite.connect("db/autoreact.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS autoreact (
                guild_id INTEGER,
                trigger TEXT,
                emojis TEXT
            )
        """)
        await db.commit()

        async with db.execute("SELECT trigger, emojis FROM autoreact WHERE guild_id = ?", (guild_id,)) as cursor:
            rows = await cursor.fetchall()

    triggers = [AutoReactTrigger(trigger=row[0], emojis=row[1]) for row in rows]
    return AutoReactConfig(guild_id=str(guild_id), triggers=triggers)


# ========== INVC ROLE (Voice Role) ==========

@router.get("/{guild_id}/invcrole", response_model=InvcConfig, summary="Get Invc Role config")
async def get_guild_invcrole(guild_id: int):
    db = await db_manager.get_connection('db/invc.db')
    # Use execute instead of with for shared connection
    await db.execute("""
        CREATE TABLE IF NOT EXISTS vcroles (
            guild_id INTEGER PRIMARY KEY,
            role_id INTEGER NOT NULL,
            enabled INTEGER DEFAULT 0
        )
    """)
    try:
        await db.execute("ALTER TABLE vcroles ADD COLUMN enabled INTEGER DEFAULT 0")
    except:
        pass
    await db.commit()

    cursor = await db.execute("SELECT role_id, enabled FROM vcroles WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    
    role_id = str(row['role_id']) if row and row['role_id'] and row['role_id'] != 0 else None
    enabled = bool(row['enabled']) if row else False
    return InvcConfig(guild_id=str(guild_id), role_id=role_id, enabled=enabled)

@router.patch("/{guild_id}/invcrole", summary="Update Invc Role config")
async def patch_guild_invcrole(guild_id: int, data: InvcUpdate):
    db = await db_manager.get_connection('db/invc.db')
    
    # Get existing row to merge
    cursor = await db.execute("SELECT role_id, enabled FROM vcroles WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    
    current_role = row['role_id'] if row else 0
    current_enabled = row['enabled'] if row else 0
    
    # Update values only if they are provided in the request
    # If data.role_id is None, it could mean 'unset' (if sent as null) or 'no change' (if omitted).
    # Given our dashboard sends the full object, we treat None as unset if it matches our frontend's behavior.
    new_role = current_role
    if data.role_id is not None:
        try:
            new_role = int(data.role_id) if data.role_id and data.role_id != "none" else 0
        except:
            new_role = 0
    elif data.role_id is None:
        # In our dash, null means "No Role Selected"
        new_role = 0

    new_enabled = current_enabled
    if data.enabled is not None:
        new_enabled = 1 if data.enabled else 0

    await db.execute("INSERT OR REPLACE INTO vcroles (guild_id, role_id, enabled) VALUES (?, ?, ?)", 
                     (guild_id, new_role, new_enabled))
    await db.commit()
    return {"status": "success"}


# ========== AUTO REACT ==========

@router.get("/{guild_id}/autoreact", response_model=AutoReactConfig, summary="Get AutoReact config")
async def get_guild_autoreact(guild_id: int):
    import aiosqlite
    async with aiosqlite.connect("db/autoreact.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS autoreact (
                guild_id INTEGER,
                trigger TEXT,
                emojis TEXT
            )
        """)
        await db.commit()

        async with db.execute("SELECT trigger, emojis FROM autoreact WHERE guild_id = ?", (guild_id,)) as cursor:
            rows = await cursor.fetchall()

    triggers = [AutoReactTrigger(trigger=row[0], emojis=row[1]) for row in rows]
    return AutoReactConfig(guild_id=str(guild_id), triggers=triggers)

@router.patch("/{guild_id}/autoreact", summary="Update AutoReact config")
async def patch_guild_autoreact(guild_id: int, data: AutoReactUpdate):
    db = await db_manager.get_connection("db/autoreact.db")
    await db.execute("""
        CREATE TABLE IF NOT EXISTS autoreact (
            guild_id INTEGER,
            trigger TEXT,
            emojis TEXT
        )
    """)
    await db.execute("DELETE FROM autoreact WHERE guild_id = ?", (guild_id,))
    for t in data.triggers:
        await db.execute("INSERT INTO autoreact (guild_id, trigger, emojis) VALUES (?, ?, ?)",
                         (guild_id, t.trigger, t.emojis))
    await db.commit()
    return {"status": "success"}


# ========== INVITES LEADERBOARD ==========

@router.get("/{guild_id}/invites", response_model=InvitesLeaderboard, summary="Get invite leaderboard")
async def get_guild_invites(guild_id: int):
    table_name = f"invites_{guild_id}"
    data_list = []
    
    db = await db_manager.get_connection("db/invite.db")
    # Check if table exists
    async with db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)) as cursor:
        exists = await cursor.fetchone()
    
    if exists:
        try:
            # Use a safer query that handles missing columns if necessary
            async with db.execute(f"SELECT user_id, total, fake, left, rejoin FROM [{table_name}] ORDER BY total DESC LIMIT 20") as cursor:
                rows = await cursor.fetchall()
            for row in rows:
                data_list.append(InviteStat(
                    user_id=str(row[0]),
                    total=row[1] or 0,
                    fake=row[2] or 0,
                    left=row[3] or 0,
                    rejoin=row[4] or 0
                ))
        except Exception as e:
            print(f"Error fetching invites for {guild_id}: {e}")
    else:
        # If no tracking data yet, just return empty list
        pass
    
    return InvitesLeaderboard(guild_id=str(guild_id), data=data_list)


# ========== REACTION ROLES ==========

@router.get("/{guild_id}/reactionroles", response_model=RRConfig, summary="Get Reaction Roles config")
async def get_guild_rr(guild_id: int):
    db = await db_manager.get_connection("rr.db")
    await db.execute("""
        CREATE TABLE IF NOT EXISTS reaction_roles (
            guild_id INTEGER,
            message_id INTEGER,
            emoji TEXT,
            role_id INTEGER
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS rr_settings (
            guild_id INTEGER PRIMARY KEY,
            dm_enabled INTEGER DEFAULT 1
        )
    """)
    await db.commit()

    async with db.execute("SELECT dm_enabled FROM rr_settings WHERE guild_id = ?", (guild_id,)) as cursor:
        dm_row = await cursor.fetchone()
    dm_enabled = dm_row[0] == 1 if dm_row else True
    
    async with db.execute("SELECT message_id, emoji, role_id FROM reaction_roles WHERE guild_id = ?", (guild_id,)) as cursor:
        rows = await cursor.fetchall()
    
    roles_list = [
        ReactionRoleEntry(
            message_id=str(row[0]),
            emoji=row[1],
            role_id=str(row[2])
        ) for row in rows
    ]
    
    return RRConfig(guild_id=str(guild_id), dm_enabled=dm_enabled, roles=roles_list)

@router.patch("/{guild_id}/reactionroles", summary="Update Reaction Roles config")
async def patch_guild_rr(guild_id: int, data: RRUpdate):
    db = await db_manager.get_connection("rr.db")
    await db.execute("""
        CREATE TABLE IF NOT EXISTS reaction_roles (
            guild_id INTEGER,
            message_id INTEGER,
            emoji TEXT,
            role_id INTEGER
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS rr_settings (
            guild_id INTEGER PRIMARY KEY,
            dm_enabled INTEGER DEFAULT 1
        )
    """)
    
    if data.dm_enabled is not None:
        await db.execute("INSERT OR REPLACE INTO rr_settings (guild_id, dm_enabled) VALUES (?, ?)",
                         (guild_id, 1 if data.dm_enabled else 0))
    
    if data.add_role is not None:
        msg_id = int(data.add_role.message_id)
        role_id = int(data.add_role.role_id)
        await db.execute("INSERT INTO reaction_roles (guild_id, message_id, emoji, role_id) VALUES (?, ?, ?, ?)",
                         (guild_id, msg_id, data.add_role.emoji, role_id))
    
    if data.remove_role_message_id is not None and data.remove_role_emoji is not None:
        msg_id = int(data.remove_role_message_id)
        await db.execute("DELETE FROM reaction_roles WHERE guild_id = ? AND message_id = ? AND emoji = ?",
                         (guild_id, msg_id, data.remove_role_emoji))
    
    await db.commit()
    return {"status": "success"}



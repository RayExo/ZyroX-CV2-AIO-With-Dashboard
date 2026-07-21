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

from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Optional

# --- Bot Schemas ---

class BotInfo(BaseModel):
    name: str
    id: Optional[str]
    guilds: int
    users: int
    commands: int
    latency: str

class BotStatus(BaseModel):
    user: str
    id: Optional[str]
    latency: float
    guild_count: int
    user_count: int
    shards: Optional[int]

# --- Guild Schemas ---

class GuildSummary(BaseModel):
    id: str
    name: str
    icon_url: Optional[str]
    owner_id: str
    member_count: int

class GuildDetails(BaseModel):
    id: str
    name: str
    icon: Optional[str]
    owner_id: str
    member_count: int
    role_count: int
    channel_count: int

class DiscordChannel(BaseModel):
    id: str
    name: str
    type: str

class DiscordRole(BaseModel):
    id: str
    name: str
    color: int
    position: int # text, voice, category, etc.

# --- Module Configurations ---

class PrefixConfig(BaseModel):
    guild_id: int
    prefix: str

class AutomodConfig(BaseModel):
    guild_id: int
    enabled: bool
    punishments: Dict[str, str]
    ignored_roles: List[int]
    ignored_channels: List[int]
    logging_channel: Optional[int]

class TicketCategory(BaseModel):
    name: str
    emoji: Optional[str]
    staff_roles: List[int] = []
    button_style: Optional[int] = 2 # Blurple
    discord_category_id: Optional[int] = None

class TicketEmbed(BaseModel):
    title: Optional[str]
    description: Optional[str]
    color: Optional[int] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class TicketConfig(BaseModel):
    guild_id: int
    panel_channel: Optional[int]
    panel_message: Optional[int]
    logging_channel: Optional[int] = None
    closed_category: Optional[int] = None
    panel_type: Optional[str] = "button"
    embed: TicketEmbed
    categories: List[TicketCategory]
    staff_roles: List[int]
    open_ticket_count: int

class LevelingEmbedStyle(BaseModel):
    color: str
    thumbnail: bool = False
    image: Optional[str] = None

class LevelingConfig(BaseModel):
    guild_id: int
    enabled: bool
    xp_per_message: int
    cooldown: int
    level_up_channel: Optional[int]
    embed_style: LevelingEmbedStyle

class LoggingConfig(BaseModel):
    guild_id: int
    log_enabled: Dict[str, bool]
    log_channels: Dict[str, int]
    ignore_channels: List[int]
    ignore_roles: List[int]
    ignore_users: List[int]
    auto_delete_duration: Optional[int]

class WelcomeEmbedData(BaseModel):
    message: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    footer_text: Optional[str] = None
    footer_icon: Optional[str] = None
    author_name: Optional[str] = None
    author_icon: Optional[str] = None
    thumbnail: Optional[str] = None
    image: Optional[str] = None

class WelcomeConfig(BaseModel):
    guild_id: int
    welcome_type: Optional[str] = None
    welcome_message: Optional[str] = None
    channel_id: Optional[str] = None
    embed_data: Optional[WelcomeEmbedData] = None
    auto_delete_duration: Optional[int] = None

class AntiNukeConfig(BaseModel):
    guild_id: int
    status: bool
    whitelisted_users: List[str] = []

class VerificationConfig(BaseModel):
    guild_id: int
    verification_channel_id: Optional[str] = None
    verified_role_id: Optional[str] = None
    log_channel_id: Optional[str] = None
    verification_method: Optional[str] = "both"
    enabled: Optional[bool] = True

class TrackingConfig(BaseModel):
    guild_id: int
    channel_id: Optional[int] = None

class TrackingUpdate(BaseModel):
    channel_id: Optional[int] = None

class J2CConfig(BaseModel):
    guild_id: str
    join_channel_id: Optional[str] = None
    control_channel_id: Optional[str] = None
    category_id: Optional[str] = None

class J2CUpdate(BaseModel):
    join_channel_id: Optional[str] = None
    control_channel_id: Optional[str] = None
    category_id: Optional[str] = None

class JoinDMConfig(BaseModel):
    guild_id: str
    message: Optional[str] = None

class JoinDMUpdate(BaseModel):
    message: Optional[str] = None

class CustomRoleConfig(BaseModel):
    guild_id: str
    staff: Optional[str] = None
    girl: Optional[str] = None
    vip: Optional[str] = None
    guest: Optional[str] = None
    frnd: Optional[str] = None
    reqrole: Optional[str] = None

class CustomRoleUpdate(BaseModel):
    staff: Optional[str] = None
    girl: Optional[str] = None
    vip: Optional[str] = None
    guest: Optional[str] = None
    frnd: Optional[str] = None
    reqrole: Optional[str] = None

class AutoReactTrigger(BaseModel):
    trigger: str
    emojis: str

class AutoReactConfig(BaseModel):
    guild_id: str
    triggers: List[AutoReactTrigger] = []

class AutoReactUpdate(BaseModel):
    triggers: List[AutoReactTrigger]

class InvcConfig(BaseModel):
    guild_id: str
    role_id: Optional[str] = None
    enabled: bool = False

class InvcUpdate(BaseModel):
    role_id: Optional[str] = None
    enabled: Optional[bool] = None

class ReactionRoleEntry(BaseModel):
    message_id: str
    emoji: str
    role_id: str

class RRConfig(BaseModel):
    guild_id: str
    dm_enabled: bool
    roles: List[ReactionRoleEntry] = []

class RRUpdate(BaseModel):
    dm_enabled: Optional[bool] = None
    add_role: Optional[ReactionRoleEntry] = None
    remove_role_message_id: Optional[str] = None
    remove_role_emoji: Optional[str] = None

class InviteStat(BaseModel):
    user_id: str
    total: int
    fake: int
    left: int
    rejoin: int

class InvitesLeaderboard(BaseModel):
    guild_id: str
    data: List[InviteStat]

# --- Update Schemas (Input) ---

class VerificationUpdate(BaseModel):
    verification_channel_id: Optional[str] = None
    verified_role_id: Optional[str] = None
    log_channel_id: Optional[str] = None
    verification_method: Optional[str] = None
    enabled: Optional[bool] = None

class VanityRoleSetup(BaseModel):
    vanity: str
    role_id: str
    log_channel_id: str

class AutoRoleConfig(BaseModel):
    guild_id: str
    bots: List[str]
    humans: List[str]

class AutoRoleUpdate(BaseModel):
    bots: Optional[List[str]] = None
    humans: Optional[List[str]] = None

class AntiNukeUpdate(BaseModel):
    status: Optional[bool] = None
    add_whitelist: Optional[str] = None
    remove_whitelist: Optional[str] = None


class WelcomeUpdate(BaseModel):
    welcome_type: Optional[str] = None
    welcome_message: Optional[str] = None
    channel_id: Optional[str] = None
    embed_data: Optional[WelcomeEmbedData] = None
    auto_delete_duration: Optional[int] = None

class PrefixUpdate(BaseModel):
    prefix: str

class TicketUpdate(BaseModel):
    panel_channel: Optional[int] = None
    logging_channel: Optional[int] = None
    closed_category: Optional[int] = None
    panel_type: Optional[str] = None
    embed_title: Optional[str] = None
    embed_description: Optional[str] = None
    embed_color: Optional[int] = None
    embed_image_url: Optional[str] = None
    embed_thumbnail_url: Optional[str] = None
    categories: Optional[List[TicketCategory]] = None
    staff_roles: Optional[List[int]] = None

class AutomodUpdate(BaseModel):
    enabled: Optional[bool] = None
    punishments: Optional[Dict[str, str]] = None
    ignored_roles: Optional[List[int]] = None
    ignored_channels: Optional[List[int]] = None
    logging_channel: Optional[int] = None

class LevelingUpdate(BaseModel):
    enabled: Optional[bool] = None
    xp_per_message: Optional[int] = None
    cooldown: Optional[int] = None
    level_up_channel: Optional[int] = None
    embed_color: Optional[str] = None

class LoggingUpdate(BaseModel):
    log_enabled: Optional[Dict[str, bool]] = None
    log_channels: Optional[Dict[str, int]] = None

class LeaderboardEntry(BaseModel):
    user_id: str
    name: str
    level: int
    xp: int

# --- Admin Schemas ---

class AdminNodeStatus(BaseModel):
    name: str
    status: str
    load: str
    icon: str # Icon identifier

class AdminStats(BaseModel):
    total_users: str
    active_servers: str
    api_latency: str
    db_size: str
    nodes: List[AdminNodeStatus]

class AdminConfig(BaseModel):
    maintenance_mode: bool
    global_notification: Optional[str] = None

class AdminConfigUpdate(BaseModel):
    maintenance_mode: Optional[bool] = None
    global_notification: Optional[str] = None

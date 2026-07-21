/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║                                                                  ║
 * ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
 * ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
 * ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
 * ║                                                                  ║
 * ║           © 2026 CodeX Devs — All Rights Reserved               ║
 * ║                                                                  ║
 * ║   discord  ──  https://discord.gg/codexdev                      ║
 * ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
 * ║   github   ──  https://github.com/RayExo                        ║
 * ║                                                                  ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

export interface BotInfo {
  name: string;
  id: number | null;
  guilds: number;
  users: number;
  commands: number;
  latency: string;
}

export interface BotStatus {
  user: string;
  id: number | null;
  latency: number;
  guild_count: number;
  user_count: number;
  shards: number | null;
}

export interface GuildSummary {
  id: number;
  name: string;
  icon_url: string | null;
  owner_id: number;
  member_count: number;
}

export interface GuildDetails {
  id: number;
  name: string;
  icon: string | null;
  owner_id: number;
  member_count: number;
  role_count: number;
  channel_count: number;
}

export interface PrefixConfig {
  guild_id: number;
  prefix: string;
}

export interface AutomodConfig {
  guild_id: number;
  enabled: boolean;
  punishments: Record<string, string>;
  ignored_roles: number[];
  ignored_channels: number[];
  logging_channel: number | null;
}

export interface TicketCategory {
  name: string;
  emoji: string | null;
  staff_roles: number[];
  button_style?: number;
  discord_category_id?: string | null;
}

export interface TicketEmbed {
  title: string | null;
  description: string | null;
  color?: number | null;
  image_url?: string | null;
  thumbnail_url?: string | null;
}

export interface TicketConfig {
  guild_id: string;
  panel_channel: string | null;
  panel_message: string | null;
  logging_channel?: string | null;
  closed_category?: string | null;
  panel_type?: string;
  embed: TicketEmbed;
  categories: TicketCategory[];
  staff_roles: number[];
  open_ticket_count: number;
}

export interface LevelingEmbedStyle {
  color: string;
  thumbnail: boolean;
  image: string | null;
}

export interface LevelingConfig {
  guild_id: number;
  enabled: boolean;
  xp_per_message: number;
  cooldown: number;
  level_up_channel: number | null;
  embed_style: LevelingEmbedStyle;
}

export interface LoggingConfig {
  guild_id: number;
  log_enabled: Record<string, boolean>;
  log_channels: Record<string, number>;
  ignore_channels: number[];
  ignore_roles: number[];
  ignore_users: number[];
  auto_delete_duration: number | null;
}

// Update Request Types
export interface PrefixUpdate {
  prefix: string;
}

export interface AutomodUpdate {
  enabled?: boolean;
  punishments?: Record<string, string>;
  ignored_roles?: number[];
  ignored_channels?: number[];
  logging_channel?: number;
}

export interface LevelingUpdate {
  enabled?: boolean;
  xp_per_message?: number;
  cooldown?: number;
  level_up_channel?: number;
  embed_color?: string;
}

export interface LoggingUpdate {
  log_enabled?: Record<string, boolean>;
  log_channels?: Record<string, number>;
}

export interface LeaderboardEntry {
  user_id: number;
  name: string;
  level: number;
  xp: number;
}

export interface DiscordChannel {
  id: string;
  name: string;
  type: string;
}

export interface DiscordRole {
  id: string;
  name: string;
  color: number;
  position: number;
}

export interface TicketUpdate {
  panel_channel?: string | null;
  logging_channel?: string | null;
  closed_category?: string | null;
  panel_type?: string;
  embed_title?: string | null;
  embed_description?: string | null;
  embed_color?: number | null;
  embed_image_url?: string | null;
  embed_thumbnail_url?: string | null;
  categories?: TicketCategory[];
}

export interface WelcomeEmbedData {
  message?: string | null;
  title?: string | null;
  description?: string | null;
  color?: string | null;
  footer_text?: string | null;
  footer_icon?: string | null;
  author_name?: string | null;
  author_icon?: string | null;
  thumbnail?: string | null;
  image?: string | null;
}

export interface WelcomeConfig {
  guild_id: number;
  welcome_type?: string | null;
  welcome_message?: string | null;
  channel_id?: string | null;
  embed_data?: WelcomeEmbedData | null;
  auto_delete_duration?: number | null;
}

export interface WelcomeUpdate {
  welcome_type?: string | null;
  welcome_message?: string | null;
  channel_id?: number | null;
  embed_data?: WelcomeEmbedData | null;
  auto_delete_duration?: number | null;
}

export interface AntiNukeConfig {
  guild_id: number;
  status: boolean;
  whitelisted_users?: string[];
}

export interface AntiNukeUpdate {
  status?: boolean;
  add_whitelist?: string;
  remove_whitelist?: string;
}

export interface VerificationConfig {
  guild_id: number;
  verification_channel_id: string | null;
  verified_role_id: string | null;
  log_channel_id: string | null;
  verification_method: string;
  enabled: boolean;
}

export interface VerificationUpdate {
  verification_channel_id?: string | null;
  verified_role_id?: string | null;
  log_channel_id?: string | null;
  verification_method?: string | null;
  enabled?: boolean | null;
}

export interface VanityRoleSetup {
  vanity: string;
  role_id: string;
  log_channel_id: string;
}

export interface AutoRoleConfig {
  guild_id: string;
  bots: string[];
  humans: string[];
}

export interface AutoRoleUpdate {
  bots?: string[];
  humans?: string[];
}

export interface AdminNodeStatus {
  name: string;
  status: string;
  load: string;
  icon: string;
}

export interface AdminStats {
  total_users: string;
  active_servers: string;
  api_latency: string;
  db_size: string;
  nodes: AdminNodeStatus[];
}

export interface AdminConfig {
  maintenance_mode: boolean;
  global_notification: string | null;
}

export interface AdminConfigUpdate {
  maintenance_mode?: boolean;
  global_notification?: string | null;
}

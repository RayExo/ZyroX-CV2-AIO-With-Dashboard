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
from discord.ext import commands, tasks
from discord import app_commands, ui, File
from mcstatus import JavaServer, BedrockServer
import aiosqlite
import os
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import asyncio
import base64
from utils.emoji import SUCCESS, ERROR, WARNING_UNICODE, CLOCK, REFRESH, JAVA_COFFEE

# --- Updated Asset Paths ---
ASSETS_DIR = "assets"
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "minecraft.ttf")
BACKGROUND_PATH = os.path.join(ASSETS_DIR, "background", "background.png")
DB_PATH = "db/minecraft.db"

# --- Other Constants ---
REFRESH_COOLDOWN_SECONDS = 30
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 125

# --- Emojis (imported from utils.emoji) ---
EMOJI_STATUS_ONLINE = "🟢"
EMOJI_STATUS_OFFLINE = "🔴"
EMOJI_PLAYERS = "👥"
EMOJI_INFO = "💻"
EMOJI_SUCCESS = SUCCESS
EMOJI_ERROR = ERROR
EMOJI_WARNING = WARNING_UNICODE
EMOJI_CLOCK = CLOCK
EMOJI_REFRESH = REFRESH
EMOJI_JAVA = JAVA_COFFEE
EMOJI_BEDROCK = "📱"
EMOJI_PROXY = "🔌"

class SetupModal(ui.Modal, title="Minecraft Server Setup"):
    server_ip = ui.TextInput(label="Enter Server IP Address", placeholder="e.g., play.hypixel.net", required=True)
    server_port = ui.TextInput(label="Enter Server Port (Optional)", placeholder="Leave blank for default ports", required=False)

    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        ip, port_str = self.server_ip.value.strip(), self.server_port.value.strip()
        port = int(port_str) if port_str.isdigit() else None
        detected_type, status, _ = await self.cog.auto_detect_server(ip, port)
        if not detected_type or not status or not status['online']:
            await interaction.followup.send(f"{EMOJI_ERROR} Could not reach or identify the server. Check IP/Port and try again.", ephemeral=True)
            return
        embed, file, view = await self.cog.generate_response(interaction.guild, detected_type, ip, port, interaction.user.id)
        sent_message = await interaction.channel.send(embed=embed, file=file, view=view)
        await self.cog.save_status_message(interaction.guild.id, interaction.user.id, interaction.channel.id, sent_message.id, detected_type, ip, port)
        await interaction.followup.send(f"{EMOJI_SUCCESS} Auto-updating status for `{ip}` set up!", ephemeral=True)

class MinecraftView(ui.View):
    def __init__(self, bot, server_type, ip, port, user_id):
        super().__init__(timeout=None)
        self.bot, self.server_type, self.ip, self.port, self.user_id = bot, server_type, ip, port, user_id
        self.last_refresh = None

    @ui.button(label="Refresh", style=discord.ButtonStyle.secondary, custom_id="refresh_button", emoji=EMOJI_REFRESH)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{EMOJI_ERROR} You can't refresh this panel.", ephemeral=True)
        now = datetime.utcnow()
        if self.last_refresh and (now - self.last_refresh).total_seconds() < REFRESH_COOLDOWN_SECONDS:
            return await interaction.response.send_message(f"{EMOJI_CLOCK} On cooldown. Wait `{REFRESH_COOLDOWN_SECONDS}` seconds.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        cog = self.bot.get_cog("Minecraft")
        embed, file, view = await cog.generate_response(interaction.guild, self.server_type, self.ip, self.port, self.user_id)
        await interaction.message.edit(embed=embed, attachments=[file] if file else [], view=view)
        await interaction.followup.send(f"{EMOJI_SUCCESS} Status refreshed.", ephemeral=True)
        self.last_refresh = now

class Minecraft(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(FONT_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(BACKGROUND_PATH), exist_ok=True)
        self.bot.loop.create_task(self.init_db())
        self.refresh_all_statuses.start()

    async def init_db(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS mc_status_messages (
                    guild_id INTEGER PRIMARY KEY, user_id INTEGER, channel_id INTEGER,
                    message_id INTEGER, server_type TEXT, server_ip TEXT, server_port INTEGER
                )""")
            await db.commit()

    def clean_motd(self, motd: str) -> str:
        return re.sub(r'§.', '', motd).strip()

    async def auto_detect_server(self, ip: str, port: int = None):
        try:
            java_port = port or 25565
            server = JavaServer(ip, java_port)
            status = await asyncio.wait_for(server.async_status(tries=1), timeout=5)
            version_name = status.version.name.lower()
            detected_type = 'velocity' if 'velocity' in version_name else 'bungeecord' if 'bungee' in version_name else 'java'
            favicon = getattr(status, 'favicon', None)
            motd_raw = status.description
            full_text = "".join(part.get('text', '') for part in motd_raw.get('extra', [])) or motd_raw.get('text', '') if isinstance(motd_raw, dict) else str(motd_raw)
            status_data = {
                "motd": self.clean_motd(full_text) or "A Minecraft Server",
                "players_online": status.players.online, "players_max": status.players.max,
                "players_sample": status.players.sample, "version": status.version.name, "online": True}
            return detected_type, status_data, favicon
        except Exception:
            pass
        try:
            bedrock_port = port or 19132
            server = BedrockServer(ip, bedrock_port)
            status = await asyncio.wait_for(server.async_status(tries=1), timeout=5)
            status_data = {
                "motd": self.clean_motd(status.motd) or "A Minecraft Server",
                "players_online": status.players.online, "players_max": status.players.max,
                "players_sample": None, "version": status.version.name, "online": True}
            return 'bedrock', status_data, None
        except Exception:
            pass
        return None, {"online": False}, None
    
    async def create_status_image(self, status_data, ip, port, server_type, server_icon_b64):
        try:
            bg = Image.open(BACKGROUND_PATH).convert("RGBA")
            img = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT))
            for i in range(0, img.width, bg.width):
                for j in range(0, img.height, bg.height): img.paste(bg, (i, j))
            draw = ImageDraw.Draw(img)
            font_large, font_medium, font_small = ImageFont.truetype(FONT_PATH, 24), ImageFont.truetype(FONT_PATH, 20), ImageFont.truetype(FONT_PATH, 16)
            if server_icon_b64:
                icon_data = base64.b64decode(server_icon_b64.split(',')[-1])
                icon_img = Image.open(io.BytesIO(icon_data)).convert("RGBA").resize((80, 80), Image.Resampling.LANCZOS)
                img.paste(icon_img, (20, (CANVAS_HEIGHT - 80) // 2), icon_img)
            default_port = 25565 if server_type != 'bedrock' else 19132
            full_ip = f"{ip}:{port}" if port and port != default_port else ip
            draw.text((120, 15), f"IP: {full_ip}", font=font_medium, fill=(255, 255, 255))
            player_text = f"{status_data.get('players_online', 0)}/{status_data.get('players_max', 0)}"
            bbox = draw.textbbox((0, 0), player_text, font=font_medium)
            draw.text((CANVAS_WIDTH - (bbox[2] - bbox[0]) - 20, 15), player_text, font=font_medium, fill=(255, 255, 255))
            motd = (status_data.get('motd', 'Offline') or "A Minecraft Server").split('')[0]
            bbox = draw.textbbox((0,0), motd, font=font_large)
            draw.text(((CANVAS_WIDTH - (bbox[2] - bbox[0])) // 2, 60), motd, font=font_large, fill=(0, 255, 255))
            power_text = "Powered by STACY"
            bbox = draw.textbbox((0,0), power_text, font=font_small)
            draw.text((CANVAS_WIDTH - (bbox[2] - bbox[0]) - 15, CANVAS_HEIGHT - 25), power_text, font=font_small, fill=(170, 170, 170))
            buffer = io.BytesIO()
            img.save(buffer, "PNG")
            buffer.seek(0)
            return File(buffer, filename="status.png")
        except FileNotFoundError: return None
        except Exception: return None

    async def generate_response(self, guild, server_type, ip, port, user_id):
        _, status, favicon = await self.auto_detect_server(ip, port)
        if not status: status = {'online': False}
        file = await self.create_status_image(status, ip, port, server_type, favicon)
        is_online = status.get("online", False)
        embed = discord.Embed(title=f"{EMOJI_STATUS_ONLINE if is_online else EMOJI_STATUS_OFFLINE} Minecraft Server Status", color=discord.Color.dark_green() if is_online else discord.Color.red())
        
        default_port = 25565 if server_type != 'bedrock' else 19132
        full_ip = f"{ip}:{port}" if port and port != default_port else ip
        type_emoji_map = {'java': EMOJI_JAVA, 'bedrock': EMOJI_BEDROCK, 'velocity': EMOJI_PROXY, 'bungeecord': EMOJI_PROXY}
        type_emoji = type_emoji_map.get(server_type, EMOJI_INFO)
        
        info_value = (f"**IP:** `{full_ip}`\n"
                      f"**Type:** {type_emoji} {server_type.capitalize()}\n"
                      f"**Version:** `{status.get('version', 'Unknown')}`\n")
        embed.add_field(name=f"{EMOJI_INFO} Server Information", value=info_value, inline=False)
        
        players_online = status.get('players_online', 0)
        players_max = status.get('players_max', 0)
        player_list_str = f"**Online:** `{players_online}/{players_max}`\n"
        player_sample = status.get('players_sample')
        if player_sample:
            player_names = [player.name for player in player_sample]
            player_list_str += "\n".join(f"`{i+1}.` {name}" for i, name in enumerate(player_names[:10]))
            if len(player_names) > 10:
                player_list_str += f"*...and {len(player_names) - 10} more*"
        elif is_online:
             player_list_str += "*Player list is hidden or unavailable.*"
        
        embed.add_field(name=f"{EMOJI_PLAYERS} Players", value=player_list_str, inline=False)
        
        if file:
            embed.set_image(url="attachment://status.png")
        
        embed.set_footer(text="Last updated")
        embed.timestamp = datetime.utcnow()
        view = MinecraftView(self.bot, server_type, ip, port, user_id)
        return embed, file, view

    async def save_status_message(self, guild_id, user_id, channel_id, message_id, server_type, ip, port):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO mc_status_messages (guild_id, user_id, channel_id, message_id, server_type, server_ip, server_port)
                VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(guild_id) DO UPDATE SET
                user_id=excluded.user_id, channel_id=excluded.channel_id, message_id=excluded.message_id,
                server_type=excluded.server_type, server_ip=excluded.server_ip, server_port=excluded.server_port
            """, (guild_id, user_id, channel_id, message_id, server_type, ip, port))
            await db.commit()

    async def delete_status_message(self, guild_id):
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT channel_id, message_id FROM mc_status_messages WHERE guild_id = ?", (guild_id,))
            if row := await cursor.fetchone():
                try:
                    channel = await self.bot.fetch_channel(row[0]); msg = await channel.fetch_message(row[1]); await msg.delete()
                except (discord.NotFound, discord.Forbidden): pass
                await db.execute("DELETE FROM mc_status_messages WHERE guild_id = ?", (guild_id,)); await db.commit()
                return True
            return False

    @tasks.loop(minutes=2)
    async def refresh_all_statuses(self):
        await self.bot.wait_until_ready()
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT guild_id, user_id, channel_id, message_id, server_type, server_ip, server_port FROM mc_status_messages") as cursor:
                async for row in cursor:
                    try:
                        guild = self.bot.get_guild(row[0])
                        if not guild: continue
                        channel = guild.get_channel(row[2])
                        if not channel: continue
                        message = await channel.fetch_message(row[3])
                        embed, file, view = await self.generate_response(guild, row[4], row[5], row[6], row[1])
                        await message.edit(embed=embed, attachments=[file] if file else [], view=view)
                        await asyncio.sleep(2)
                    except discord.NotFound: await self.delete_status_message(row[0])
                    except Exception as e: print(f"Auto-refresh error for guild {row[0]}: {e}")

    minecraft = app_commands.Group(name="minecraft", description="Commands for Minecraft server status.")

    @minecraft.command(name="setup", description="Set up the auto-updating Minecraft server status.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_slash(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB_PATH) as db:
            if await (await db.execute("SELECT 1 FROM mc_status_messages WHERE guild_id = ?", (interaction.guild.id,))).fetchone():
                return await interaction.response.send_message(f"{EMOJI_WARNING} Setup already exists. Use `/minecraft reset`.", ephemeral=True)
        await interaction.response.send_modal(SetupModal(self))

    @minecraft.command(name="reset", description="Remove the Minecraft server status setup.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reset_slash(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        removed = await self.delete_status_message(interaction.guild.id)
        await interaction.followup.send(f"{EMOJI_SUCCESS} Minecraft status panel removed." if removed else f"{EMOJI_WARNING} No setup found.", ephemeral=True)
            
    @minecraft.command(name="status", description="Get a one-time status of the configured server.")
    async def status_slash(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        async with aiosqlite.connect(DB_PATH) as db:
            row = await (await db.execute("SELECT server_type, server_ip, server_port, user_id FROM mc_status_messages WHERE guild_id = ?", (interaction.guild.id,))).fetchone()
        if not row:
            return await interaction.followup.send(f"{EMOJI_WARNING} No server configured. Use `/minecraft setup`.", ephemeral=True)
        embed, file, _ = await self.generate_response(interaction.guild, row[0], row[1], row[2], row[3])
        await interaction.followup.send(embed=embed, file=file, ephemeral=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Minecraft(bot))
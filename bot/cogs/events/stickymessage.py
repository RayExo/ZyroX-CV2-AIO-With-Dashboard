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
import aiosqlite
import json
import asyncio
from discord.ext import commands
from utils.config import *

class StickyMessageListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.processing_channels = set()
        self.last_processed = {}

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if not hasattr(message, "guild") or message.guild is None:
            return

        if message.channel.id in self.processing_channels:
            return

        async with aiosqlite.connect("db/stickymessages.db") as db:
            cursor = await db.execute("""
                SELECT id, message_type, message_content, embed_data, last_message_id,
                       enabled, delay_seconds, auto_delete_after, ignore_bots, 
                       ignore_commands, trigger_count, current_count
                FROM sticky_messages 
                WHERE guild_id = ? AND channel_id = ? AND enabled = 1
            """, (message.guild.id, message.channel.id))
            sticky_data = await cursor.fetchone()

        if not sticky_data:
            return

        (
            sticky_id, msg_type, msg_content, embed_data, last_msg_id,
            enabled, delay_seconds, auto_delete_after, ignore_bots,
            ignore_commands, trigger_count, current_count
        ) = sticky_data

        if ignore_bots and message.author.bot:
            return

        if ignore_commands and message.content.startswith(await self.get_prefix(message)):
            return

        self.processing_channels.add(message.channel.id)

        try:
            new_count = current_count + 1

            if new_count >= trigger_count:
                await self.update_counter(message.guild.id, message.channel.id, 0)

                if last_msg_id:
                    try:
                        old_message = await message.channel.fetch_message(last_msg_id)
                        await old_message.delete()
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        pass

                await asyncio.sleep(delay_seconds)

                new_sticky_msg = await self.send_sticky_message(
                    message.channel, msg_type, msg_content, embed_data
                )

                if new_sticky_msg:
                    async with aiosqlite.connect("db/stickymessages.db") as db:
                        await db.execute("""
                            UPDATE sticky_messages 
                            SET last_message_id = ?
                            WHERE guild_id = ? AND channel_id = ?
                        """, (new_sticky_msg.id, message.guild.id, message.channel.id))
                        await db.commit()

                    if auto_delete_after > 0:
                        asyncio.create_task(
                            self.auto_delete_message(new_sticky_msg, auto_delete_after)
                        )
            else:
                await self.update_counter(message.guild.id, message.channel.id, new_count)

        except Exception:
            pass
        finally:
            self.processing_channels.discard(message.channel.id)

    async def get_prefix(self, message):
        try:
            async with aiosqlite.connect("db/prefix.db") as db:
                cursor = await db.execute(
                    "SELECT prefix FROM prefix WHERE guild_id = ?",
                    (message.guild.id,)
                )
                result = await cursor.fetchone()
                return result[0] if result else "!"
        except:
            return "!"

    async def update_counter(self, guild_id, channel_id, new_count):
        async with aiosqlite.connect("db/stickymessages.db") as db:
            await db.execute("""
                UPDATE sticky_messages 
                SET current_count = ?
                WHERE guild_id = ? AND channel_id = ?
            """, (new_count, guild_id, channel_id))
            await db.commit()

    async def send_sticky_message(self, channel, msg_type, msg_content, embed_data):
        try:
            if msg_type == "plain" and msg_content:
                return await channel.send(content=msg_content)

            elif msg_type == "embed" and embed_data:
                try:
                    data = json.loads(embed_data)
                    embed = discord.Embed(color=discord.Color.red())

                    if data.get("title"):
                        embed.title = data["title"]

                    if data.get("description"):
                        embed.description = data["description"]

                    if data.get("color"):
                        try:
                            color_str = data["color"]
                            if color_str.startswith("#"):
                                embed.color = discord.Color(
                                    int(color_str.lstrip("#"), 16)
                                )
                        except:
                            embed.color = discord.Color.red()

                    if data.get("footer"):
                        embed.set_footer(text=data["footer"])
                    else:
                        embed.set_footer(text=f"{BRAND_NAME} Development")

                    embed.timestamp = discord.utils.utcnow()
                    return await channel.send(embed=embed)

                except json.JSONDecodeError:
                    return await channel.send(content="*[Embed data corrupted]*")

        except (discord.Forbidden, discord.HTTPException):
            pass
        except Exception:
            pass

        return None

    async def auto_delete_message(self, message, delay):
        try:
            await asyncio.sleep(delay)
            await message.delete()
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        try:
            async with aiosqlite.connect("db/stickymessages.db") as db:
                await db.execute(
                    "DELETE FROM sticky_messages WHERE channel_id = ?",
                    (channel.id,)
                )
                await db.commit()
        except:
            pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            async with aiosqlite.connect("db/stickymessages.db") as db:
                await db.execute(
                    "DELETE FROM sticky_messages WHERE guild_id = ?",
                    (guild.id,)
                )
                await db.execute(
                    "DELETE FROM sticky_settings WHERE guild_id = ?",
                    (guild.id,)
                )
                await db.commit()
        except:
            pass

async def setup(bot):
    await bot.add_cog(StickyMessageListener(bot))
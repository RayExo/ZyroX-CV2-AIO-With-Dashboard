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
import aiohttp
import aiosqlite
import asyncio
import logging
from discord.ext import commands
from core import zyrox, Cog
from utils.config import *

DATABASE_PATH = 'db/autorole.db'
logger = logging.getLogger(__name__)

class Autorole2(Cog):
    def __init__(self, bot: zyrox):
        self.bot = bot
        self.headers = {"Authorization": f"Bot {self.bot.http.token}"}

    async def get_autorole(self, guild_id: int):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT bots, humans FROM autorole WHERE guild_id = ?", (guild_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    bots, humans = row
                    bots = [int(role_id) for role_id in bots.replace('[', '').replace(']', '').replace(' ', '').split(',') if role_id]
                    humans = [int(role_id) for role_id in humans.replace('[', '').replace(']', '').split(',') if role_id]
                    return {"bots": bots, "humans": humans}
                else:
                    return {"bots": [], "humans": []}

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await self.get_autorole(member.guild.id)
        bot_roles = data["bots"]
        human_roles = data["humans"]

        if member.bot:
            roles_to_add = bot_roles
        else:
            roles_to_add = human_roles

        for role_id in roles_to_add:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason=f"{BRAND_NAME} | Autoroles")
                except discord.Forbidden:
                    print(f"Bot lacks permissions to add role in a guild during Autorole Event .")
                except discord.HTTPException as e:
                    if e.status == 429:
                        retry_after = e.response.headers.get('Retry-After')
                        if retry_after:
                            retry_after = float(retry_after)
                            print(f"(Autorole) Rate limit encountered. Retrying after {retry_after} seconds.")
                            await asyncio.sleep(retry_after)
                            await member.add_roles(role, reason=f"{BRAND_NAME} | Autoroles")
                except discord.errors.RateLimited as e:
                    print(f"Rate limit encountered: {e}. Retrying in {e.retry_after} seconds.")
                    await asyncio.sleep(e.retry_after)
                    await member.add_roles(role, reason=f"{BRAND_NAME} | Autoroles")
                except Exception as e:
                    logger.error(f"Unexpected error in Autorole: {e}")


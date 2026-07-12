import discord
from discord.ext import commands
import aiosqlite
import asyncio
import datetime
import pytz

class AntiWebhookCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_limits = {}
        self.cooldowns = {}

    async def fetch_audit_logs(self, guild, action, target_id):
        try:
            now = datetime.datetime.now(pytz.utc)
            logs = [entry async for entry in guild.audit_logs(action=action, limit=1)]
            for entry in logs:
                if entry.target.id == target_id:
                    difference = (now - entry.created_at).total_seconds() * 1000
                    if difference < 3600000:  
                        return entry
        except Exception:
            return None
        return None

    def can_fetch_audit(self, guild_id, event_name, max_requests=6, interval=10, cooldown_duration=300):
        now = datetime.datetime.now()
        self.event_limits.setdefault(guild_id, {}).setdefault(event_name, []).append(now)

        timestamps = self.event_limits[guild_id][event_name]
        timestamps = [t for t in timestamps if (now - t).total_seconds() <= interval]
        self.event_limits[guild_id][event_name] = timestamps

        if guild_id in self.cooldowns and event_name in self.cooldowns[guild_id]:
            if (now - self.cooldowns[guild_id][event_name]).total_seconds() < cooldown_duration:
                return False
            del self.cooldowns[guild_id][event_name]

        if len(timestamps) > max_requests:
            self.cooldowns.setdefault(guild_id, {})[event_name] = now
            return False

        return True

    async def is_blacklisted_guild(self, guild_id):
        async with aiosqlite.connect('db/block.db') as block_db:
            cursor = await block_db.execute("SELECT 1 FROM guild_blacklist WHERE guild_id = ?", (str(guild_id),))
            return await cursor.fetchone() is not None

    @commands.Cog.listener()
    async def on_webhooks_create(self, channel):
        guild = channel.guild
        if await self.is_blacklisted_guild(guild.id):
            return

        async with aiosqlite.connect('db/anti.db') as db:
            async with db.execute("SELECT status FROM antinuke WHERE guild_id = ?", (guild.id,)) as cursor:
                antinuke_status = await cursor.fetchone()

            if not antinuke_status or not antinuke_status[0]:
                return

        if not self.can_fetch_audit(guild.id, 'webhook_create'):
            return

        entry = await self.fetch_audit_logs(guild, discord.AuditLogAction.webhook_create, channel.id)
        if entry is None:
            return

        executor = entry.user

        if executor.id in {guild.owner_id, self.bot.user.id}:
            return

        async with aiosqlite.connect('db/anti.db') as db:
            async with db.execute("SELECT mngweb FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", 
                                  (guild.id, executor.id)) as cursor:
                whitelist_status = await cursor.fetchone()

            if whitelist_status and whitelist_status[0]:
                return

            async with db.execute("SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?", 
                                  (guild.id, executor.id)) as cursor:
                extra_owner_status = await cursor.fetchone()

            if extra_owner_status and extra_owner_status[0]:
                return

            try:
                await self.ban_executor_and_delete_webhook(guild, executor, entry.target)
                await asyncio.sleep(3)
            except Exception:
                return

    async def ban_executor_and_delete_webhook(self, guild, executor, webhook):
        retries = 3
        while retries > 0:
            try:
                await guild.ban(executor, reason="Webhook Create | Unwhitelisted User")
                if webhook:
                    await webhook.delete(reason="Webhook Created by unwhitelisted user")
                return
            except discord.Forbidden:
                return
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        await asyncio.sleep(float(retry_after))
                else:
                    return
            except discord.errors.RateLimited as e:
                await asyncio.sleep(e.retry_after)
                retries -= 1
            except Exception:
                return

            retries -= 1

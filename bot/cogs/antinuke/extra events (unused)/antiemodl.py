import discord
from discord.ext import commands
import aiosqlite
import asyncio
import random
import datetime

class AntiEmojiDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_audit_logs(self, guild, action):
        try:
            await asyncio.sleep(random.uniform(0.5, 2.0))
            logs = [entry async for entry in guild.audit_logs(action=action, limit=1, after=datetime.datetime.utcnow() - datetime.timedelta(seconds=3))]
            if logs:
                return logs[0]
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = e.response.headers.get('Retry-After')
                if retry_after:
                    retry_after = float(retry_after)
                    await asyncio.sleep(retry_after)
                    return await self.fetch_audit_logs(guild, action)
        except Exception as e:
            print(f"An error occurred while fetching audit logs: {e}")
        return None

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        if len(after) < len(before):
            async with aiosqlite.connect('db/anti.db') as db:
                async with db.execute("SELECT status FROM antinuke WHERE guild_id = ?", (guild.id,)) as cursor:
                    antinuke_status = await cursor.fetchone()

                if not antinuke_status or not antinuke_status[0]:
                    return

                logs = await self.fetch_audit_logs(guild, discord.AuditLogAction.emoji_delete)
                if logs is None:
                    return

                executor = logs.user
                difference = discord.utils.utcnow() - logs.created_at
                if difference.total_seconds() > 3600:
                    return

                if executor.id in {guild.owner_id, self.bot.user.id}:
                    return

                async with db.execute("SELECT mngstemo FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", (guild.id, executor.id)) as cursor:
                    whitelist_status = await cursor.fetchone()

                if whitelist_status and whitelist_status[0]:
                    return

                async with db.execute("SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?", (guild.id, executor.id)) as cursor:
                    extra_owner_status = await cursor.fetchone()

                if extra_owner_status:
                    return

                await self.kick_executor(guild, executor)

    async def kick_executor(self, guild, executor):
        retries = 3
        while retries > 0:
            try:
                await guild.kick(executor, reason="Emoji Delete | Unwhitelisted User")
                return
            except discord.Forbidden:
                print(f"Failed to kick {executor.id} due to missing permissions.")
                return
            except discord.HTTPException as e:
                print(f"Failed to kick {executor.id} due to HTTPException: {e}")
                if e.status == 429:
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        retry_after = float(retry_after)
                        print(f"Rate limit encountered while kicking. Retrying after {retry_after} seconds.")
                        await asyncio.sleep(retry_after)
                        retries -= 1
                    else:
                        return
                else:
                    return
            except discord.errors.RateLimited as e:
                print(f"Rate limit encountered while kicking: {e}. Retrying in {e.retry_after} seconds.")
                await asyncio.sleep(e.retry_after)
                retries -= 1
            except Exception as e:
                print(f"An unexpected error occurred while kicking {executor.id}: {e}")
                return

        print(f"Failed to kick {executor.id} after multiple attempts due to rate limits.")

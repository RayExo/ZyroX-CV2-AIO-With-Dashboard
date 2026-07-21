import discord
from discord.ext import commands
import aiosqlite
from datetime import timedelta, datetime
import asyncio

class AntiUnban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_audit_logs(self, guild, action, target_id):
        try:
            async for entry in guild.audit_logs(limit=1, action=action):
                if entry.target.id == target_id:
                    return entry
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = e.response.headers.get('Retry-After')
                if retry_after:
                    retry_after = float(retry_after)
                    await asyncio.sleep(retry_after)
                    return await self.fetch_audit_logs(guild, action, target_id)
        except Exception as e:
            print(f"An error occurred while fetching audit logs: {e}")
        return None

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        async with aiosqlite.connect('db/anti.db') as db:
            async with db.execute("SELECT status FROM antinuke WHERE guild_id = ?", (guild.id,)) as cursor:
                antinuke_status = await cursor.fetchone()

            if not antinuke_status or not antinuke_status[0]:
                return

            log_entry = await self.fetch_audit_logs(guild, discord.AuditLogAction.unban, user.id)
            if log_entry is None:
                return

            executor = log_entry.user

            if executor.id in {guild.owner_id, self.bot.user.id}:
                return

            async with db.execute("SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?", (guild.id, executor.id)) as cursor:
                extra_owner_status = await cursor.fetchone()

            if extra_owner_status:
                return

            async with db.execute("SELECT ban FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", (guild.id, executor.id)) as cursor:
                whitelist_status = await cursor.fetchone()

            if whitelist_status and whitelist_status[0]:
                return

            await self.ban_executor(guild, executor, user)

    async def ban_executor(self, guild, executor, user):
        retries = 3
        while retries > 0:
            try:
                await guild.ban(executor, reason="Member Unban | Unwhitelisted User")
                await guild.ban(user, reason="Reverting unban by unwhitelisted user")
                return
            except discord.Forbidden:
                print(f"Failed to ban {executor.id} or user due to missing permissions.")
                return
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        retry_after = float(retry_after)
                        print(f"Rate limit encountered. Retrying after {retry_after} seconds.")
                        await asyncio.sleep(retry_after)
                else:
                    print(f"HTTPException encountered: {e}")
                    return
            except discord.errors.RateLimited as e:
                print(f"Rate limit encountered while banning: {e}. Retrying in {e.retry_after} seconds.")
                await asyncio.sleep(e.retry_after)
            except Exception as e:
                print(f"An unexpected error occurred while banning {executor.id} or user: {e}")
                return

            retries -= 1

        print(f"Failed to ban {executor.id} after multiple attempts due to rate limits.")

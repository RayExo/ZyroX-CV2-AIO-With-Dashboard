import discord
from discord.ext import commands
import aiosqlite
import asyncio
import datetime
from datetime import timedelta

class AntiEveryone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_limits = {}

    async def can_message_delete(self, guild_id, event_name, max_requests=5, interval=10, cooldown_duration=300):
        now = datetime.datetime.now()
        self.event_limits.setdefault(guild_id, {}).setdefault(event_name, []).append(now)

        timestamps = self.event_limits[guild_id][event_name]
        timestamps = [t for t in timestamps if (now - t).total_seconds() <= interval]
        self.event_limits[guild_id][event_name] = timestamps

        if len(timestamps) > max_requests:
            return False

        return True

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or not message.mention_everyone:
            return

        guild = message.guild

        async with aiosqlite.connect('db/anti.db') as db:
            async with db.execute("SELECT status FROM antinuke WHERE guild_id = ?", (guild.id,)) as cursor:
                antinuke_status = await cursor.fetchone()

            if not antinuke_status or not antinuke_status[0]:
                return

            if message.author.id in {guild.owner_id, self.bot.user.id}:
                return

            async with db.execute("SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?", (guild.id, message.author.id)) as cursor:
                extraowner_status = await cursor.fetchone()

            if extraowner_status:
                return

            async with db.execute("SELECT meneve FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", (guild.id, message.author.id)) as cursor:
                whitelist_status = await cursor.fetchone()

            if whitelist_status and whitelist_status[0]:
                return

            
            if not await self.can_message_delete(guild.id, 'mention_everyone'):
                return

            try:
                await self.timeout_user(message.author)
                await self.delete_everyone_messages(message.channel)
            except Exception as e:
                print(f"An unexpected error occurred while handling {message.author.id}: {e}")

    async def timeout_user(self, user):
        retries = 3
        duration = 60 * 60  
        while retries > 0:
            try:
                await user.edit(timed_out_until=discord.utils.utcnow() + timedelta(seconds=duration), reason="Mentioned Everyone/Here | Unwhitelisted User")
                return  
            except discord.Forbidden:
                return
            except discord.HTTPException as e:
                print(f"Failed to timeout {user.id} due to HTTPException: {e}")
                if e.status == 429:
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        retry_after = float(retry_after)
                        print(f"Rate limit encountered while timing out. Retrying after {retry_after} seconds.")
                        await asyncio.sleep(retry_after)
                        retries -= 1
                else:
                    return
            except discord.errors.RateLimited as e:
                print(f"Rate limit encountered while timing out: {e}. Retrying in {e.retry_after} seconds.")
                await asyncio.sleep(e.retry_after)
                retries -= 1
            except Exception as e:
                print(f"An unexpected error occurred while timing out {user.id}: {e}")
                return

        print(f"Failed to timeout {user.id} after multiple attempts due to rate limits.")

    async def delete_everyone_messages(self, channel):
        retries = 3
        while retries > 0:
            try:
                async for msg in channel.history(limit=100):
                    if msg.mention_everyone:
                        await msg.delete()
                        await asyncio.sleep(3)  
                return  
            except discord.Forbidden:
                return
            except discord.HTTPException as e:
                print(f"Failed to delete messages due to HTTPException: {e}")
                if e.status == 429:
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        retry_after = float(retry_after)
                        print(f"Rate limit encountered while deleting messages. Retrying after {retry_after} seconds.")
                        await asyncio.sleep(retry_after)
                        retries -= 1
                else:
                    return
            except discord.errors.RateLimited as e:
                print(f"Rate limit encountered while deleting messages: {e}. Retrying in {e.retry_after} seconds.")
                await asyncio.sleep(e.retry_after)
                retries -= 1
            except Exception as e:
                print(f"An unexpected error occurred while deleting messages: {e}")
                return

        print(f"Failed to delete messages after multiple attempts due to rate limits.")

import discord
from discord.ext import commands
import sqlite3
from datetime import datetime

class Messagespack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addmessages", aliases=["addmsg"])
    @commands.has_permissions(manage_messages=True)
    async def addmessages(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("Amount must be greater than 0.")
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        conn = sqlite3.connect("db/messages.db")
        c = conn.cursor()

        c.execute("SELECT count FROM messages WHERE guild_id = ? AND user_id = ? AND date = ?",
                  (ctx.guild.id, member.id, today))
        result = c.fetchone()

        if result:
            c.execute("UPDATE messages SET count = count + ? WHERE guild_id = ? AND user_id = ? AND date = ?",
                      (amount, ctx.guild.id, member.id, today))
        else:
            c.execute("INSERT INTO messages (guild_id, user_id, date, count) VALUES (?, ?, ?, ?)",
                      (ctx.guild.id, member.id, today, amount))

        conn.commit()
        conn.close()
        await ctx.send(f"Added {amount} messages to {member.mention} for today.")

    @commands.command(name="removemessages", aliases=["removemsg"])
    @commands.has_permissions(manage_messages=True)
    async def removemessages(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("Amount must be greater than 0.")

        today = datetime.utcnow().strftime("%Y-%m-%d")
        conn = sqlite3.connect("db/messages.db")
        c = conn.cursor()

        c.execute("SELECT count FROM messages WHERE guild_id = ? AND user_id = ? AND date = ?",
                  (ctx.guild.id, member.id, today))
        result = c.fetchone()

        if result:
            new_count = max(0, result[0] - amount)
            c.execute("UPDATE messages SET count = ? WHERE guild_id = ? AND user_id = ? AND date = ?",
                      (new_count, ctx.guild.id, member.id, today))
            conn.commit()
            await ctx.send(f"Removed {amount} messages from {member.mention} for today.")
        else:
            await ctx.send(f"{member.mention} has no messages recorded for today.")
        conn.close()

    @commands.command(name="clearmessage", aliases=["clearmsg"])
    @commands.has_permissions(manage_messages=True)
    async def clearmessage(self, ctx, member: discord.Member):
        conn = sqlite3.connect("db/messages.db")
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE guild_id = ? AND user_id = ?",
                  (ctx.guild.id, member.id))
        conn.commit()
        conn.close()
        await ctx.send(f"All messages cleared for {member.mention}.")
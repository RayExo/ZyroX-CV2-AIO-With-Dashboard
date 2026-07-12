import time
import discord
from discord.ext import commands
import asyncio
from utils.Tools import *
from datetime import datetime

class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="timer", aliases=['tstart'], description="Starts a timer")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def _timer(self, ctx, times, *, title: str = None):
        if title is None:
            title = 'Timer'

        try:
            try:
                time = int(times)
            except:
                convertTimeList = {'s':1, 'm':60, 'h':3600, 'd':86400, 'S':1, 'M':60, 'H':3600, 'D':86400}
                time = int(times[:-1]) * convertTimeList[times[-1]]
            if time > 86400:
                await ctx.send("Timers should not exceed a day in duration.")
                return
            if time <= 0:
                await ctx.send("Timers do not go into negatives.")
                return
            if time >= 3600:
                embed = discord.Embed(
                    title=f'{title}',
                    description=f"**{time//3600}** hours, **{time%3600//60}** minutes, **{time%60}** seconds",
                    color=0xFF0000
                )
                embed.set_footer(text=f'Requested by {ctx.author.name}')
                message = await ctx.send(embed=embed)
                await message.add_reaction('⏱️')
            elif time >= 60:
                embed = discord.Embed(
                    title=f'{title}',
                    description=f"**{time//60}** minutes, **{time%60}** seconds",
                    color=0xFF0000
                )
                embed.set_footer(text=f'Requested by {ctx.author.name}')
                message = await ctx.send(embed=embed)
                await message.add_reaction('⏱️')
            elif time < 60:
                embed = discord.Embed(
                    title=f'{title}',
                    description=f'**{time}** seconds',
                    color=0xFF0000
                )
                embed.set_footer(text=f'Requested by {ctx.author.name}')
                message = await ctx.send(embed=embed)
                await message.add_reaction('⏱️')
            while True:
                try:
                    await asyncio.sleep(6)
                    time -= 6
                    if time >= 3600:
                        embed = discord.Embed(
                            title=f'{title}',
                            description=f"**{time//3600}** hours, **{time%3600//60}** minutes, **{time%60}** seconds",
                            color=0xFF0000
                        )
                        embed.set_footer(text=f'Requested by {ctx.author.name}')
                        await message.edit(embed=embed)
                    elif time >= 60:
                        embed = discord.Embed(
                            title=f'{title}',
                            description=f"**{time//60}** minutes, **{time%60}** seconds",
                            color=0xFF0000
                        )
                        embed.set_footer(text=f'Requested by {ctx.author.name}')
                        await message.edit(embed=embed)
                    elif time < 60:
                        embed = discord.Embed(
                            title=f'{title}',
                            description=f"**{time}** seconds",
                            color=0xFF0000
                        )
                        embed.set_footer(text=f'Requested by {ctx.author.name}')
                        await message.edit(embed=embed)
                    if time <= 0:
                        embed = discord.Embed(
                            title=f'{title}',
                            description='Time is up!',
                            color=0xFF0000
                        )
                        content= ctx.author.mention
                        await message.edit(content=content, embed=embed)
                        m = await ctx.channel.get_message(message.id)
                        list_thingy = []
                        output_list_thingy = []
                        reactants = await m.reactions[0].users().flatten()
                        reactants.pop(reactants.index(self.client.user))
                        for user in reactants:
                            list_thingy.append(user.id)
                            x = '<@!' + str(user.id) + '>' 
                            output_list_thingy.append(x)
                        if output_list_thingy != []:
                            final = ', '.join(map(str, output_list_thingy))
                            return await ctx.send(f'The timer for **{title}** has ended!\n{final}')
                        else:
                            return await ctx.send(f'The timer for **{title}** has ended!')
                except:
                    break
        except ValueError:
            await ctx.send(f"Invalid time input.", delete_after=5)

 
from __future__ import annotations

from typing import Optional
import time
import random
import asyncio

import discord
from discord.ext import commands

from .utils import DiscordColor, DEFAULT_COLOR


class ReactionGame:
    """
    Reaction Game
    """

    def __init__(self, emoji: str = "🖱️") -> None:
        self.emoji = emoji

    async def wait_for_reaction(
        self, ctx: commands.Context[commands.Bot], *, timeout: float
    ) -> tuple[discord.User, float]:
        start = time.perf_counter()

        def check(reaction: discord.Reaction, _: discord.User) -> bool:
            return (
                str(reaction.emoji) == self.emoji and reaction.message == self.message
            )

        _, user = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=check)
        end = time.perf_counter()

        return user, (end - start)

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        timeout: Optional[float] = None,
        embed_color: DiscordColor = DEFAULT_COLOR,
    ) -> discord.Message:
        """
        starts the reaction game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        timeout : Optional[float], optional
            the timeout for when waiting, by default None
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR

        Returns
        -------
        discord.Message
            returns the game message
        """
        embed = discord.Embed(
            title="Reaction Game",
            description=f"React with {self.emoji} when the embed is edited!",
            color=discord.Color.random(),
        )

        self.message = await ctx.send(embed=embed)
        await self.message.add_reaction(self.emoji)

        pause = random.uniform(1.0, 5.0)
        await asyncio.sleep(pause)

        embed.description = f"React with {self.emoji} now!"
        await self.message.edit(embed=embed)

        try:
            user, elapsed = await self.wait_for_reaction(ctx, timeout=timeout)
        except asyncio.TimeoutError:
            return self.message

        embed.description = f"{user.mention} reacted first in `{elapsed:.2f}s` !"
        await self.message.edit(embed=embed)

        return self.message

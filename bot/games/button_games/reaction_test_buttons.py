from __future__ import annotations

from typing import Optional, Union
import time
import random
import asyncio

import discord
from discord.ext import commands

from ..utils import DiscordColor, DEFAULT_COLOR, BaseView


class ReactionButton(discord.ui.Button["ReactionView"]):
    def __init__(self, style: discord.ButtonStyle) -> None:
        super().__init__(label="\u200b", style=style)

        self.edited: bool = False
        self.clicked: bool = False

    async def callback(self, interaction: discord.Interaction) -> None:
        game = self.view.game

        if game.author_only and interaction.user != game.author:
            return await interaction.response.send_message(
                "This game is only for the author!", ephemeral=True
            )

        if not self.edited or self.clicked:
            return await interaction.response.defer()
        else:
            end_time = time.perf_counter()
            elapsed = end_time - self.view.game.start_time

            game.embed.description = (
                f"{interaction.user.mention} reacted first in `{elapsed:.2f}s` !"
            )
            await interaction.response.edit_message(embed=game.embed)

            self.clicked = True
            return game.finished_event.set()


class ReactionView(BaseView):
    game: BetaReactionGame

    def __init__(
        self,
        game: BetaReactionGame,
        *,
        button_style: discord.ButtonStyle,
        timeout: float,
    ) -> None:

        super().__init__(timeout=timeout)

        self.game = game
        self.button_style = button_style
        self.button = ReactionButton(self.button_style)
        self.add_item(self.button)


class BetaReactionGame:
    """
    Reaction(buttons) game
    """

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        author_only: bool = False,
        pause_range: tuple[float, float] = (1.0, 5.0),
        start_button_style: discord.ButtonStyle = discord.ButtonStyle.blurple,
        end_button_style: Union[
            discord.ButtonStyle, tuple[discord.ButtonStyle, ...]
        ] = (discord.ButtonStyle.green, discord.ButtonStyle.red),
        embed_color: DiscordColor = DEFAULT_COLOR,
        timeout: Optional[float] = None,
    ) -> discord.Message:
        """
        starts the Reaction(buttons) Game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        author_only : bool, optional
            specifies whether or not tjhe view is only limited to the author, by default False
        pause_range : tuple[float, float], optional
            the time range to randomly pause for, by default (1.0, 5.0)
        start_button_style : discord.ButtonStyle, optional
            specifies the button style to start with, by default discord.ButtonStyle.blurple
        end_button_style : Union[discord.ButtonStyle, tuple[discord.ButtonStyle, ...]], optional
            specifies the button styles(s) to change to, by default (discord.ButtonStyle.green, discord.ButtonStyle.red)
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        timeout : Optional[float], optional
            the timeout for the view, by default None

        Returns
        -------
        discord.Message
            returns the game message
        """
        self.finished_event = asyncio.Event()

        self.author_only = author_only
        self.author = ctx.author

        self.embed = discord.Embed(
            title="Reaction Game",
            description=f"Click the button below, when the button changes color!",
            color=discord.Color.random(),
        )
        self.view = ReactionView(self, button_style=start_button_style, timeout=timeout)
        self.message = await ctx.send(embed=self.embed, view=self.view)

        pause = random.uniform(*pause_range)
        await asyncio.sleep(pause)

        if isinstance(end_button_style, tuple):
            self.view.button.style = random.choice(end_button_style)
        else:
            self.view.button.style = end_button_style

        await self.message.edit(view=self.view)
        self.start_time = time.perf_counter()
        self.view.button.edited = True

        await self.finished_event.wait()
        return self.message

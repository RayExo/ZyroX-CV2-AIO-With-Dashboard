from __future__ import annotations

from typing import Optional, ClassVar
import random
import asyncio

import discord
from discord.ext import commands

from ..utils import *


class MemoryButton(discord.ui.Button["MemoryView"]):
    def __init__(self, emoji: str, *, style: discord.ButtonStyle, row: int = 0) -> None:
        self.value = emoji

        super().__init__(
            label="\u200b",
            style=style,
            row=row,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        game = self.view.game

        if opened := self.view.opened:
            game.moves += 1
            game.embed.set_field_at(0, name="\u200b", value=f"Moves: `{game.moves}`")

            self.emoji = self.value
            self.disabled = True
            await interaction.response.edit_message(view=self.view)

            if opened.value != self.value:
                await asyncio.sleep(self.view.pause_time)

                opened.emoji = None
                opened.disabled = False

                self.emoji = None
                self.disabled = False
                self.view.opened = None
            else:
                self.view.opened = None

                if all(
                    button.disabled
                    for button in self.view.children
                    if isinstance(button, discord.ui.Button)
                ):
                    await interaction.message.edit(
                        content="Game Over, Congrats!", view=self.view
                    )
                    return self.view.stop()

            return await interaction.message.edit(view=self.view, embed=game.embed)
        else:
            self.emoji = self.value
            self.view.opened = self
            self.disabled = True
            return await interaction.response.edit_message(view=self.view)


class MemoryView(BaseView):
    board: list[list[str]]
    DEFAULT_ITEMS: ClassVar[list[str]] = [
        "🥝",
        "🍓",
        "🍹",
        "🍋",
        "🥭",
        "🍎",
        "🍊",
        "🍍",
        "🍑",
        "🍇",
        "🍉",
        "🥬",
    ]

    def __init__(
        self,
        game: MemoryGame,
        items: list[str],
        *,
        button_style: discord.ButtonStyle,
        pause_time: float,
        timeout: Optional[float] = None,
    ) -> None:

        super().__init__(timeout=timeout)

        self.game = game

        self.button_style = button_style
        self.pause_time = pause_time
        self.opened: Optional[MemoryButton] = None

        if not items:
            items = self.DEFAULT_ITEMS[:]
        assert len(items) == 12

        items *= 2
        random.shuffle(items)
        random.shuffle(items)
        items.insert(12, None)

        self.board = chunk(items, count=5)

        for i, row in enumerate(self.board):
            for item in row:
                button = MemoryButton(item, style=self.button_style, row=i)

                if not item:
                    button.disabled = True
                self.add_item(button)


class MemoryGame:
    """
    Memory Game
    """

    def __init__(self) -> None:
        self.embed_color: Optional[DiscordColor] = None
        self.embed: Optional[discord.Embed] = None
        self.moves: int = 0

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        embed_color: DiscordColor = DEFAULT_COLOR,
        items: list[str] = [],
        pause_time: float = 0.7,
        button_style: discord.ButtonStyle = discord.ButtonStyle.red,
        timeout: Optional[float] = None,
    ) -> discord.Message:
        """
        starts the memory game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        items : list[str], optional
            items to use for the game tiles, by default []
        pause_time : float, optional
            specifies the duration to pause for before hiding the tiles again, by default 0.7
        button_style : discord.ButtonStyle, optional
            the primary button style to use, by default discord.ButtonStyle.red
        timeout : Optional[float], optional
            the timeout for the view, by default None

        Returns
        -------
        discord.Message
            returns the game message
        """
        self.embed_color = discord.Color.random()
        self.embed = discord.Embed(
            description="**Memory Game**", color=discord.Color.random()
        )
        self.embed.add_field(name="\u200b", value="Moves: `0`")

        self.view = MemoryView(
            game=self,
            items=items,
            button_style=button_style,
            pause_time=pause_time,
            timeout=timeout,
        )
        self.message = await ctx.send(embed=self.embed, view=self.view)

        await double_wait(
            wait_for_delete(ctx, self.message),
            self.view.wait(),
        )
        return self.message

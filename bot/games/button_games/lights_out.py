from __future__ import annotations

import random
from typing import Any, TYPE_CHECKING, Optional, Literal, Final

import discord
from discord.ext import commands

from .number_slider import SlideView
from ..utils import *

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    Board: TypeAlias = list[list[Optional[Literal["💡"]]]]

BULB: Final[Literal["💡"]] = "💡"


class LightsOutButton(discord.ui.Button["LightsOutView"]):
    def __init__(
        self, emoji: str, *, style: discord.ButtonStyle, row: int, col: int
    ) -> None:
        super().__init__(
            emoji=emoji,
            label="\u200b",
            style=style,
            row=row,
        )

        self.col = col

    async def callback(self, interaction: discord.Interaction) -> None:
        game = self.view.game

        if interaction.user != game.player:
            return await interaction.response.send_message(
                "This is not your game!", ephemeral=True
            )
        else:
            row, col = self.row, self.col

            beside_item = game.beside_item(row, col)
            game.toggle(row, col)

            for i, j in beside_item:
                game.toggle(i, j)

            self.view.update_board(clear=True)

            game.moves += 1
            game.embed.set_field_at(0, name="\u200b", value=f"Moves: `{game.moves}`")

            if game.tiles == game.completed:
                self.view.disable_all()
                self.view.stop()
                game.embed.description = "**Congrats! You won!**"

            return await interaction.response.edit_message(
                embed=game.embed, view=self.view
            )


class LightsOutView(SlideView):
    game: LightsOut

    def __init__(self, game: LightsOut, *, timeout: float) -> None:
        super().__init__(game, timeout=timeout)

    def update_board(self, *, clear: bool = False) -> None:

        if clear:
            self.clear_items()

        for i, row in enumerate(self.game.tiles):
            for j, tile in enumerate(row):
                button = LightsOutButton(
                    emoji=tile,
                    style=self.game.button_style,
                    row=i,
                    col=j,
                )
                self.add_item(button)


class LightsOut:
    """
    Lights Out Game
    """

    def __init__(self, count: Literal[1, 2, 3, 4, 5] = 4) -> None:

        if count not in range(1, 6):
            raise ValueError("Count must be an integer between 1 and 5")

        self.moves: int = 0
        self.count = count

        self.completed: Final[Board] = [[None] * self.count for _ in range(self.count)]
        self.tiles: Board = []

        self.player: Optional[discord.User] = None
        self.button_style: discord.ButtonStyle = discord.ButtonStyle.green

    def toggle(self, row: int, col: int) -> None:
        self.tiles[row][col] = BULB if self.tiles[row][col] is None else None

    def beside_item(self, row: int, col: int) -> list[tuple[int, int]]:
        beside = [
            (row - 1, col),
            (row, col - 1),
            (row + 1, col),
            (row, col + 1),
        ]

        data = [
            (i, j)
            for i, j in beside
            if i in range(self.count) and j in range(self.count)
        ]
        return data

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        button_style: discord.ButtonStyle = discord.ButtonStyle.green,
        embed_color: DiscordColor = DEFAULT_COLOR,
        timeout: Optional[float] = None,
    ) -> discord.Message:
        """
        starts the Lights Out Game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        button_style : discord.ButtonStyle, optional
            the primary button style to use, by default discord.ButtonStyle.green
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        timeout : Optional[float], optional
            the timeout for the view, by default None

        Returns
        -------
        discord.Message
            returns the game message
        """
        self.button_style = button_style
        self.player = ctx.author

        self.tiles = random.choices((None, BULB), k=self.count**2)
        self.tiles = chunk(self.tiles, count=self.count)

        self.view = LightsOutView(self, timeout=timeout)
        self.embed = discord.Embed(
            description="Turn off all the tiles!", color=embed_color
        )
        self.embed.add_field(name="\u200b", value="Moves: `0`")

        self.message = await ctx.send(embed=self.embed, view=self.view)

        await double_wait(
            wait_for_delete(ctx, self.message),
            self.view.wait(),
        )
        return self.message

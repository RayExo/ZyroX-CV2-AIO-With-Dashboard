from __future__ import annotations

from typing import ClassVar, Optional

import discord
from discord.ext import commands

from ..tictactoe import Tictactoe
from ..utils import *


class TTTButton(discord.ui.Button["TTTView"]):
    def __init__(self, label: str, style: discord.ButtonStyle, *, row: int, col: int):
        super().__init__(
            label=label,
            style=style,
            row=row,
        )

        self.col = col

    async def callback(self, interaction: discord.Interaction) -> None:
        user = interaction.user
        game = self.view.game

        if user not in (game.cross, game.circle):
            return await interaction.response.send_message(
                "You are not part of this game!", ephemeral=True
            )

        if user != game.turn:
            return await interaction.response.send_message(
                "it is not your turn!", ephemeral=True
            )

        self.label = game.player_to_emoji[user]
        self.disabled = True

        game.board[self.row][self.col] = self.label
        game.turn = game.circle if user == game.cross else game.cross

        tie = all(button.disabled for button in self.view.children)

        if game_over := game.is_game_over(tie=tie):
            if game.winning_indexes:
                self.view.disable_all()
                game.create_streak()
            self.view.stop()

        embed = game.make_embed(game_over=game_over or tie)
        await interaction.response.edit_message(embed=embed, view=self.view)


class TTTView(BaseView):
    def __init__(self, game: BetaTictactoe, *, timeout: float) -> None:
        super().__init__(timeout=timeout)

        self.game = game

        for x, row in enumerate(game.board):
            for y, square in enumerate(row):
                button = TTTButton(
                    label=square,
                    style=self.game.button_style,
                    row=x,
                    col=y,
                )
                self.add_item(button)


class BetaTictactoe(Tictactoe):
    """
    Tictactoe(buttons) game
    """

    BLANK: ClassVar[str] = "\u200b"
    CIRCLE: ClassVar[str] = "O"
    CROSS: ClassVar[str] = "X"

    def create_streak(self) -> None:
        chunked = chunk(self.view.children, count=3)
        for row, col in self.winning_indexes:
            button: TTTButton = chunked[row][col]
            button.style = self.win_button_style

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        button_style: discord.ButtonStyle = discord.ButtonStyle.green,
        *,
        embed_color: DiscordColor = DEFAULT_COLOR,
        win_button_style: discord.ButtonStyle = discord.ButtonStyle.red,
        timeout: Optional[float] = None,
    ) -> discord.Message:
        """
        starts the tictactoe(buttons) game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        button_style : discord.ButtonStyle, optional
            the primary button style to use, by default discord.ButtonStyle.green
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        win_button_style : discord.ButtonStyle, optional
            the button style to use to show the winning line, by default discord.ButtonStyle.red
        timeout : Optional[float], optional
            the timeout for the view, by default None

        Returns
        -------
        discord.Message
            returns the game message
        """
        self.embed_color = discord.Color.random()
        self.button_style = button_style
        self.win_button_style = win_button_style

        self.view = TTTView(self, timeout=timeout)
        self.message = await ctx.send(embed=self.make_embed(), view=self.view)

        await double_wait(
            wait_for_delete(ctx, self.message, user=(self.cross, self.circle)),
            self.view.wait(),
        )

        return self.message

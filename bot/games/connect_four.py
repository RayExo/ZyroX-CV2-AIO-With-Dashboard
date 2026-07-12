from __future__ import annotations

from typing import Optional, Union
import asyncio

import discord
from discord.ext import commands

from .utils import DiscordColor, DEFAULT_COLOR

RED = "🔴"
BLUE = "🔵"
BLANK = "⬛"


class ConnectFour:
    """
    Connect-4 Game
    """

    def __init__(self, *, red: discord.User, blue: discord.User) -> None:
        self.red_player = red
        self.blue_player = blue

        self.board: list[list[str]] = [[BLANK for _ in range(7)] for _ in range(6)]
        self._controls: tuple[str, ...] = (
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
        )

        self.turn = self.red_player
        self.message: Optional[discord.Message] = None
        self.winner: Optional[discord.User] = None

        self._conversion: dict[str, int] = {
            emoji: i for i, emoji in enumerate(self._controls)
        }
        self.player_to_emoji: dict[discord.User, str] = {
            self.red_player: RED,
            self.blue_player: BLUE,
        }
        self.emoji_to_player: dict[str, discord.User] = {
            v: k for k, v in self.player_to_emoji.items()
        }

    def board_string(self) -> str:
        board = "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n"
        for row in self.board:
            board += "".join(row) + "\n"
        return board

    def make_embed(self, *, status: bool) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.random())
        if not status:
            embed.description = f"**Turn:** {self.turn.name}\n**Piece:** `{self.player_to_emoji[self.turn]}`"
        else:
            status_ = f"{self.winner} won!" if self.winner else "Tie"
            embed.description = f"**Game over**\n{status_}"
        return embed

    def place_move(self, column: Union[str, int], user) -> list[list[str]]:

        if isinstance(column, str):
            if column not in self._controls:
                raise KeyError("Provided emoji is not one of the valid controls")

            column = self._conversion[column]

        for x in range(5, -1, -1):
            if self.board[x][column] == BLANK:
                self.board[x][column] = self.player_to_emoji[user]
                break

        self.turn = self.red_player if user == self.blue_player else self.blue_player
        return self.board

    def is_game_over(self) -> bool:

        if all(i != BLANK for i in self.board[0]):
            return True

        for x in range(6):
            for i in range(4):
                if (
                    self.board[x][i]
                    == self.board[x][i + 1]
                    == self.board[x][i + 2]
                    == self.board[x][i + 3]
                    and self.board[x][i] != BLANK
                ):
                    self.winner = self.emoji_to_player[self.board[x][i]]
                    return True

        for x in range(3):
            for i in range(7):
                if (
                    self.board[x][i]
                    == self.board[x + 1][i]
                    == self.board[x + 2][i]
                    == self.board[x + 3][i]
                    and self.board[x][i] != BLANK
                ):
                    self.winner = self.emoji_to_player[self.board[x][i]]
                    return True

        for x in range(3):
            for i in range(4):
                if (
                    self.board[x][i]
                    == self.board[x + 1][i + 1]
                    == self.board[x + 2][i + 2]
                    == self.board[x + 3][i + 3]
                    and self.board[x][i] != BLANK
                ):
                    self.winner = self.emoji_to_player[self.board[x][i]]
                    return True

        for x in range(5, 2, -1):
            for i in range(4):
                if (
                    self.board[x][i]
                    == self.board[x - 1][i + 1]
                    == self.board[x - 2][i + 2]
                    == self.board[x - 3][i + 3]
                    and self.board[x][i] != BLANK
                ):
                    self.winner = self.emoji_to_player[self.board[x][i]]
                    return True

        return False

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        timeout: Optional[float] = None,
        embed_color: DiscordColor = discord.Color.random(),
        remove_reaction_after: bool = False,
        **kwargs,
    ) -> discord.Message:
        """
        starts the Connect-4 game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        timeout : Optional[float], optional
            the timeout for when waiting, by default None
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        remove_reaction_after : bool, optional
            specifies whether or not to remove the user's move reaction, by default False

        Returns
        -------
        discord.Message
            returns the game message
        """
        self.embed_color = discord.Color.random()

        embed = self.make_embed(status=False)
        self.message = await ctx.send(self.board_string(), embed=embed, **kwargs)

        for button in self._controls:
            await self.message.add_reaction(button)

        while not ctx.bot.is_closed():

            def check(reaction: discord.Reaction, user: discord.User) -> bool:
                return (
                    str(reaction.emoji) in self._controls
                    and user == self.turn
                    and reaction.message == self.message
                    and self.board[0][self._conversion[str(reaction.emoji)]] == BLANK
                )

            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add", timeout=timeout, check=check
                )
            except asyncio.TimeoutError:
                break

            emoji = str(reaction.emoji)
            self.place_move(emoji, user)

            if status := self.is_game_over():
                break

            if remove_reaction_after:
                await self.message.remove_reaction(emoji, user)

            embed = self.make_embed(status=False)
            await self.message.edit(content=self.board_string(), embed=embed)

        embed = self.make_embed(status=status)
        await self.message.edit(content=self.board_string(), embed=embed)

        return self.message

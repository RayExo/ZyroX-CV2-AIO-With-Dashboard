# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
# ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
# ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
# ║                                                                  ║
# ║            © 2026 CodeX Devs — All Rights Reserved              ║
# ║                                                                  ║
# ║   discord  ──  https://discord.gg/codexdev                      ║
# ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
# ║   github   ──  https://github.com/RayExo                        ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

from typing import Optional, ClassVar
import asyncio

import discord
from discord.ext import commands
from utils.emoji import ERROR

from .utils import DiscordColor, DEFAULT_COLOR


class Tictactoe:
    """
    TicTacToe Game
    """

    BLANK: ClassVar[str] = "⬛"
    CIRCLE: ClassVar[str] = "⭕"
    CROSS: ClassVar[str] = ERROR
    _conversion: ClassVar[dict[str, tuple[int, int]]] = {
        "1️⃣": (0, 0),
        "2️⃣": (0, 1),
        "3️⃣": (0, 2),
        "4️⃣": (1, 0),
        "5️⃣": (1, 1),
        "6️⃣": (1, 2),
        "7️⃣": (2, 0),
        "8️⃣": (2, 1),
        "9️⃣": (2, 2),
    }

    _WINNERS: ClassVar[tuple[tuple[tuple[int, int], ...], ...]] = (
        ((0, 0), (0, 1), (0, 2)),
        ((1, 0), (1, 1), (1, 2)),
        ((2, 0), (2, 1), (2, 2)),
        ((0, 0), (1, 0), (2, 0)),
        ((0, 1), (1, 1), (2, 1)),
        ((0, 2), (1, 2), (2, 2)),
        ((0, 0), (1, 1), (2, 2)),
        ((0, 2), (1, 1), (2, 0)),
    )

    def __init__(self, cross: discord.User, circle: discord.User) -> None:
        self.cross = cross
        self.circle = circle

        self.board: list[list[str]] = [[self.BLANK for _ in range(3)] for _ in range(3)]
        self.turn: discord.User = self.cross

        self.winner: Optional[discord.User] = None
        self.winning_indexes: list[tuple[int, int]] = []
        self.message: Optional[discord.Message] = None

        self._controls: list[str] = [
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
        ]

        self.emoji_to_player: dict[discord.User, str] = {
            self.CIRCLE: self.circle,
            self.CROSS: self.cross,
        }
        self.player_to_emoji: dict[str, discord.User] = {
            v: k for k, v in self.emoji_to_player.items()
        }

    def board_string(self) -> str:
        board = ""
        for row in self.board:
            board += "".join(row) + "\n"
        return board

    def make_embed(self, *, game_over: bool = False) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.random())
        if game_over:
            status = f"{self.winner.mention} won!" if self.winner else "Tie"
            embed.description = f"**Game over**\n{status}"
        else:
            embed.description = f"**Turn:** {self.turn.mention}\n**Piece:** `{self.player_to_emoji[self.turn]}`"
        return embed

    def make_move(self, emoji: str, user: discord.User) -> list:

        if emoji not in self._controls:
            raise KeyError("Provided emoji is not one of the valid controls")
        else:
            x, y = self._conversion[emoji]
            piece = self.player_to_emoji[user]
            self.board[x][y] = piece

            self.turn = self.circle if user == self.cross else self.cross
            self._conversion.pop(emoji)
            self._controls.remove(emoji)
            return self.board

    def is_game_over(self, *, tie: bool = False) -> bool:

        for possibility in self._WINNERS:
            row = [self.board[r][c] for r, c in possibility]

            if len(set(row)) == 1 and row[0] != self.BLANK:
                self.winner = self.emoji_to_player[row[0]]
                self.winning_indexes = possibility
                return True

        if not self._controls or tie:
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
        starts the tictactoe game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        timeout : Optional[float], optional
            the timeout for when waiting, by default None
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        remove_reaction_after : bool, optional
            specifies whether or not to remove the move reaction each time, by default False

        Returns
        -------
        discord.Message
            returns the game emssage
        """
        self.embed_color = embed_color

        embed = self.make_embed()
        self.message = await ctx.send(self.board_string(), embed=embed, **kwargs)

        for button in self._controls:
            await self.message.add_reaction(button)

        while not ctx.bot.is_closed():

            def check(reaction: discord.Reaction, user: discord.User) -> bool:
                return (
                    str(reaction.emoji) in self._controls
                    and user == self.turn
                    and reaction.message == self.message
                )

            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add", timeout=timeout, check=check
                )
            except asyncio.TimeoutError:
                break

            if self.is_game_over():
                break

            emoji = str(reaction.emoji)
            self.make_move(emoji, user)
            embed = self.make_embed()

            if remove_reaction_after:
                await self.message.remove_reaction(emoji, user)

            await self.message.edit(content=self.board_string(), embed=embed)

        embed = self.make_embed(game_over=True)
        await self.message.edit(content=self.board_string(), embed=embed)

        return self.message

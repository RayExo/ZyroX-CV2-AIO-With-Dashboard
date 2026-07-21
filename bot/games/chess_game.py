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

from typing import Optional, ClassVar, Literal
import asyncio

import discord
from discord.ext import commands
import chess
from utils.emoji import SUCCESS

from .utils import DiscordColor, DEFAULT_COLOR


class Chess:
    BASE_URL: ClassVar[str] = "http://www.fen-to-image.com/image/64/double/coords/"

    def __init__(self, *, white: discord.User, black: discord.User) -> None:
        self.white = white
        self.black = black
        self.turn = self.white

        self.winner: Optional[discord.User] = None
        self.message: Optional[discord.Message] = None

        self.board: chess.Board = chess.Board()

        self.last_move: dict[str, str] = {}

    def get_color(self) -> Literal["white", "black"]:
        return "white" if self.turn == self.white else "black"

    async def make_embed(self) -> discord.Embed:
        embed = discord.Embed(title="Chess Game", color=discord.Color.random())
        embed.description = f"**Turn:** `{self.turn}`\n**Color:** `{self.get_color()}`\n**Check:** `{self.board.is_check()}`"
        embed.set_image(url=f"{self.BASE_URL}{self.board.board_fen()}")

        embed.add_field(
            name="Last Move",
            value=f"```yml\n{self.last_move.get('color', '-')}: {self.last_move.get('move', '-')}\n```",
        )
        return embed

    async def place_move(self, uci: str) -> chess.Board:
        self.last_move = {"color": self.get_color(), "move": f"{uci[:2]} -> {uci[2:]}"}

        self.board.push_uci(uci)
        self.turn = self.white if self.turn == self.black else self.black
        return self.board

    async def fetch_results(self) -> discord.Embed:
        results = self.board.result()
        embed = discord.Embed(title="Chess Game")

        if self.board.is_checkmate():
            embed.description = f"Game over\nCheckmate | Score: `{results}`"
        elif self.board.is_stalemate():
            embed.description = f"Game over\nStalemate | Score: `{results}`"
        elif self.board.is_insufficient_material():
            embed.description = f"Game over\nInsufficient material left to continue the game | Score: `{results}`"
        elif self.board.is_seventyfive_moves():
            embed.description = f"Game over\n75-moves rule | Score: `{results}`"
        elif self.board.is_fivefold_repetition():
            embed.description = f"Game over\nFive-fold repitition. | Score: `{results}`"
        else:
            embed.description = (
                f"Game over\nVariant end condition. | Score: `{results}`"
            )

        embed.set_image(url=f"{self.BASE_URL}{self.board.board_fen()}")
        return embed

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        timeout: Optional[float] = None,
        embed_color: DiscordColor = 0x000000,
        add_reaction_after_move: bool = False,
        **kwargs,
    ) -> discord.Message:
        """
        starts the chess game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        timeout : Optional[float], optional
            the timeout for when waiting, by default None
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        add_reaction_after_move : bool, optional
            specifies whether or not to add a reaction to the user's move validating it, by default False

        Returns
        -------
        Optional[discord.Message]
            returns the game message
        """
        self.embed_color = discord.Color.random()

        embed = await self.make_embed()
        self.message = await ctx.send(embed=embed, **kwargs)

        while not ctx.bot.is_closed():

            def check(m: discord.Message) -> bool:
                try:
                    if self.board.parse_uci(m.content.lower()):
                        return m.author == self.turn and m.channel == ctx.channel
                    else:
                        return False
                except ValueError:
                    return False

            try:
                message: discord.Message = await ctx.bot.wait_for(
                    "message", timeout=timeout, check=check
                )
            except asyncio.TimeoutError:
                return

            await self.place_move(message.content.lower())
            embed = await self.make_embed()

            if add_reaction_after_move:
                await message.add_reaction(SUCCESS)

            if self.board.is_game_over():
                break

            await self.message.edit(embed=embed)

        embed = await self.fetch_results()
        await self.message.edit(embed=embed)
        await ctx.send("~ Game Over ~")

        return self.message

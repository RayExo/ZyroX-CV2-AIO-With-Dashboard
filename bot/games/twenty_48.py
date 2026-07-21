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

from typing import TYPE_CHECKING, Literal, Optional
from io import BytesIO
import os
import asyncio
import random
import pathlib
import itertools

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from utils.emoji import ARROW_LEFT, ARROW_RIGHT, ARROW_UP, ARROW_DOWN, STOP_BUTTON

from .utils import *

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    Board: TypeAlias = list[list[int]]


async def create_2048_emojis(
    guild: discord.Guild, names: Optional[list[str]] = None
) -> list[discord.Emoji]:
    """
    creates 2048 emojis in the specified Guild
    intended to be ran once initially manually.

    Parameters
    ----------
    guild : discord.Guild
        the guild to create the emojis in
    names : Optional[list[str]], optional
        names to use for the emojis
        if not specified, _<number> will be used, by default None

    Returns
    -------
    list[Emoji]
        returns the list of emojis created
    """
    result: list[discord.Emoji] = []

    directory = pathlib.Path(__file__).parent / "assets/2048-emoji-asset-examples"
    files = os.listdir(directory)
    names = map(lambda n: f"_{n[:-4]}", files) if not names else names

    for name, file in zip(names, files):
        with open(os.path.join(directory, file), "rb") as fp:
            result.append(
                await guild.create_custom_emoji(
                    name=name, image=fp.read(), reason="2048 emojis"
                )
            )
    return result


class Twenty48:
    """
    Twenty48 Game
    """

    player: discord.User

    def __init__(
        self,
        number_to_display_mapping: dict[str, str] = {},
        *,
        render_image: bool = False,
    ) -> None:

        self.embed_color: Optional[DiscordColor] = None
        self.embed: Optional[discord.Embed] = None

        self.board: Board = [[0 for _ in range(4)] for _ in range(4)]
        self.message: Optional[discord.Message] = None

        self._controls = [ARROW_LEFT, ARROW_RIGHT, ARROW_UP, ARROW_DOWN]
        self._conversion = number_to_display_mapping
        self._render_image = render_image

        if self._render_image and discord.version_info.major < 2:
            raise ValueError(
                "discord.py versions under v2.0.0 do not support rendering images since editing files is new in 2.0"
            )

        if self._render_image:
            self._color_mapping: dict[str, tuple[tuple[int, int, int], int]] = {
                "0": ((204, 192, 179), 50),
                "2": ((237, 227, 217), 50),
                "4": ((237, 224, 200), 50),
                "8": ((242, 177, 121), 50),
                "16": ((245, 149, 100), 50),
                "32": ((246, 124, 95), 50),
                "64": ((246, 94, 59), 50),
                "128": ((236, 206, 113), 40),
                "256": ((236, 203, 96), 40),
                "512": ((236, 199, 80), 40),
                "1024": ((236, 196, 62), 30),
                "2048": ((236, 193, 46), 30),
                "4096": ((59, 57, 49), 30),
                "8192": ((59, 57, 49), 30),
            }

            self.LIGHT_CLR = (249, 246, 242)
            self.DARK_CLR = (119, 110, 101)
            self.BG_CLR = (187, 173, 160)

            self.BORDER_W = 20
            self.SQ_S = 100
            self.SPACE_W = 15

            self.IMG_LENGTH = self.BORDER_W * 2 + self.SQ_S * 4 + self.SPACE_W * 3

            self._font = ImageFont.truetype(
                str(pathlib.Path(__file__).parent / "assets/ClearSans-Bold.ttf"), 50
            )

    def _reverse(self, board: Board) -> Board:
        return [row[::-1] for row in board]

    def _transp(self, board: Board) -> Board:
        return [[board[i][j] for i in range(4)] for j in range(4)]

    def _merge(self, board: Board) -> Board:
        for i in range(4):
            for j in range(3):
                tile = board[i][j]
                if tile == board[i][j + 1] and tile != 0:
                    board[i][j] *= 2
                    board[i][j + 1] = 0
        return board

    def _compress(self, board: Board) -> Board:
        new_board = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            pos = 0
            for j in range(4):
                if board[i][j] != 0:
                    new_board[i][pos] = board[i][j]
                    pos += 1
        return new_board

    def move_left(self) -> None:
        stage = self._compress(self.board)
        stage = self._merge(stage)
        stage = self._compress(stage)
        self.board = stage

    def move_right(self) -> None:
        stage = self._reverse(self.board)
        stage = self._compress(stage)
        stage = self._merge(stage)
        stage = self._compress(stage)
        stage = self._reverse(stage)
        self.board = stage

    def move_up(self) -> None:
        stage = self._transp(self.board)
        stage = self._compress(stage)
        stage = self._merge(stage)
        stage = self._compress(stage)
        stage = self._transp(stage)
        self.board = stage

    def move_down(self) -> None:
        stage = self._transp(self.board)
        stage = self._reverse(stage)
        stage = self._compress(stage)
        stage = self._merge(stage)
        stage = self._compress(stage)
        stage = self._reverse(stage)
        stage = self._transp(stage)
        self.board = stage

    def spawn_new(self) -> bool:
        """
        spawns a new `2`

        Returns
        -------
        bool
            returns whether or not the game is lost
        """
        board = self.board
        zeroes = [
            (j, i) for j, sub in enumerate(board) for i, el in enumerate(sub) if el == 0
        ]

        if not zeroes:
            return True
        else:
            i, j = random.choice(zeroes)
            board[i][j] = 2
            return False

    def number_to_emoji(self) -> str:
        board = self.board
        game_string = ""

        emoji_array = [
            [self._conversion.get(str(l), f"`{l}` ") for l in row] for row in board
        ]

        for row in emoji_array:
            game_string += "".join(row) + "\n"
        return game_string

    def check_win(self) -> bool:
        flattened = itertools.chain(*self.board)

        for num in (2048, 4096, 8192):
            if num in flattened:
                if num == 2048:
                    self.embed = discord.Embed(description="", color=discord.Color.random())
                self.embed.description += f"⭐: Congrats! You hit **{num}**!\n"

                if num == self.win_at:
                    self.embed.description += "**Game Over! You Won**\n"
                    return True
        return False

    @executor()
    def render_image(self) -> discord.File:
        SQ = self.SQ_S
        with Image.new("RGB", (self.IMG_LENGTH, self.IMG_LENGTH), self.BG_CLR) as img:
            cursor = ImageDraw.Draw(img)

            x = y = self.BORDER_W
            for row in self.board:
                for tile in row:
                    tile = str(tile)
                    color, fsize = self._color_mapping.get(tile)
                    font = self._font.font_variant(size=fsize)
                    cursor.rounded_rectangle(
                        (x, y, x + SQ, y + SQ), radius=5, width=0, fill=color
                    )

                    if tile != "0":
                        text_fill = (
                            self.DARK_CLR if tile in ("2", "4") else self.LIGHT_CLR
                        )
                        cursor.text(
                            (x + SQ / 2, y + SQ / 2),
                            tile,
                            font=font,
                            anchor="mm",
                            fill=text_fill,
                        )

                    x += SQ + self.SPACE_W
                x = self.BORDER_W
                y += SQ + self.SPACE_W

            buf = BytesIO()
            img.save(buf, "PNG")
        buf.seek(0)
        return discord.File(buf, "2048.png")

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        win_at: Literal[2048, 4096, 8192] = 8192,
        timeout: Optional[float] = None,
        remove_reaction_after: bool = False,
        delete_button: bool = False,
        embed_color: DiscordColor = DEFAULT_COLOR,
        **kwargs,
    ) -> discord.Message:
        """
        starts the 2048 game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        win_at : Literal[2048, 4096, 8192], optional
            the tile to stop the game / win at, by default 8192
        timeout : Optional[float], optional
            the timeout when waiting, by default None
        remove_reaction_after : bool, optional
            specifies whether or not to remove the move reaction, by default False
        delete_button : bool, optional
            specifies whether or not to include a stop button or not, by default False
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR

        Returns
        -------
        discord.Message
            returns the game message
        """
        self.win_at = win_at
        self.embed_color = embed_color
        self.player = ctx.author

        self.board[random.randrange(4)][random.randrange(4)] = 2
        self.board[random.randrange(4)][random.randrange(4)] = 2

        if self._render_image:
            image = await self.render_image()
            self.message = await ctx.send(file=image, **kwargs)
        else:
            board_string = self.number_to_emoji()
            self.message = await ctx.send(board_string, **kwargs)

        if delete_button:
            self._controls.append(STOP_BUTTON)

        for button in self._controls:
            await self.message.add_reaction(button)

        while not ctx.bot.is_closed():

            def check(reaction: discord.Reaction, user: discord.User) -> bool:
                return (
                    str(reaction.emoji) in self._controls
                    and user == self.player
                    and reaction.message == self.message
                )

            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add", timeout=timeout, check=check
                )
            except asyncio.TimeoutError:
                break

            emoji = str(reaction.emoji)

            if delete_button and emoji == STOP_BUTTON:
                await self.message.delete()
                break

            if emoji == ARROW_RIGHT:
                self.move_right()

            elif emoji == ARROW_LEFT:
                self.move_left()

            elif emoji == ARROW_DOWN:
                self.move_down()

            elif emoji == ARROW_UP:
                self.move_up()

            if remove_reaction_after:
                try:
                    await self.message.remove_reaction(emoji, user)
                except discord.DiscordException:
                    pass

            lost = self.spawn_new()
            won = self.check_win()

            if lost:
                self.embed = discord.Embed(
                    description="Game Over! You lost.",
                    color=discord.Color.random(),
                )

            if self._render_image:
                image = await self.render_image()
                await self.message.edit(attachments=[image], embed=self.embed)
            else:
                board_string = self.number_to_emoji()
                await self.message.edit(content=board_string, embed=self.embed)

            if won or lost:
                break

        return self.message

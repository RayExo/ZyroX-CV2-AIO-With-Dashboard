from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union, ClassVar
from io import BytesIO
import asyncio
import pathlib
import random
import re

import discord
from discord.ext import commands
from PIL import Image, ImageDraw

from .utils import *

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    Coords: TypeAlias = tuple[int, int]

SHIPS: dict[str, tuple[int, tuple[int, int, int]]] = {
    "carrier": (5, (52, 152, 219)),
    "battleship": (4, (246, 246, 112)),
    "destroyer": (3, (14, 146, 150)),
    "submarine": (3, (95, 245, 80)),
    "patrol boat": (2, (190, 190, 190)),
}


class Ship:
    def __init__(
        self,
        name: str,
        size: int,
        start: Coords,
        color: tuple[int, int, int],
        vertical: bool = False,
    ) -> None:

        self.name: str = name
        self.size: int = size

        self.start: Coords = start
        self.vertical: bool = vertical
        self.color: tuple[int, int, int] = color

        self.end: Coords = (
            (self.start[0], self.start[1] + self.size - 1)
            if self.vertical
            else (self.start[0] + self.size - 1, self.start[1])
        )

        self.span: list[Coords] = (
            [(self.start[0], i) for i in range(self.start[1], self.end[1] + 1)]
            if self.vertical
            else [(i, self.start[1]) for i in range(self.start[0], self.end[0] + 1)]
        )

        self.hits: list[bool] = [False] * self.size


class Board:
    def __init__(self, player: discord.User, random: bool = True) -> None:

        self.player: discord.User = player
        self.ships: list[Ship] = []

        self.my_hits: list[Coords] = []
        self.my_misses: list[Coords] = []

        self.op_hits: list[Coords] = []
        self.op_misses: list[Coords] = []

        if random:
            self._place_ships()

    @property
    def moves(self) -> list[Coords]:
        return self.my_hits + self.my_misses

    def _is_valid(self, ship: Ship) -> bool:

        if ship.end[0] > 10 or ship.end[1] > 10:
            return False

        for existing in self.ships:
            if any(c in existing.span for c in ship.span):
                return False
        return True

    def _place_ships(self) -> None:
        def place_ship(ship: str, size: int, color: tuple[int, int, int]) -> None:
            start = random.randint(1, 10), random.randint(1, 10)
            vertical = bool(random.randint(0, 1))

            new_ship = Ship(
                name=ship,
                size=size,
                start=start,
                vertical=vertical,
                color=color,
            )

            if self._is_valid(new_ship):
                self.ships.append(new_ship)
            else:
                place_ship(ship, size, color)

        for ship, (size, color) in SHIPS.items():
            place_ship(ship, size, color)

    def won(self) -> bool:
        return all(all(ship.hits) for ship in self.ships)

    def draw_dot(
        self, cur: ImageDraw.Draw, x: int, y: int, fill: Union[int, tuple[int, ...]]
    ) -> None:
        x1, y1 = x - 10, y - 10
        x2, y2 = x + 10, y + 10
        cur.ellipse((x1, y1, x2, y2), fill=fill)

    def draw_sq(
        self, cur: ImageDraw.Draw, x: int, y: int, *, coord: Coords, ship: Ship
    ) -> None:
        vertical = ship.vertical
        left_end = ship.span.index(coord) == 0
        right_end = ship.span.index(coord) == ship.size - 1

        if vertical and left_end:
            diffs = (18, 18, 25, 18)
        elif vertical and right_end:
            diffs = (25, 18, 18, 18)
        elif not vertical and left_end:
            diffs = (18, 18, 18, 25)
        elif not vertical and right_end:
            diffs = (18, 25, 18, 18)
        elif vertical:
            diffs = (25, 18, 25, 18)
        else:
            diffs = (18, 25, 18, 25)

        d1, d2, d3, d4 = diffs
        x1, y1 = x - d1, y - d2
        x2, y2 = x + d3, y + d4
        cur.rounded_rectangle((x1, y1, x2, y2), radius=5, fill=ship.color)

    def get_ship(self, coord: Coords) -> Optional[Ship]:
        if s := [ship for ship in self.ships if coord in ship.span]:
            return s[0]

    @executor()
    def to_image(self, hide: bool = False) -> BytesIO:
        RED = (255, 0, 0)
        GRAY = (128, 128, 128)

        with Image.open(pathlib.Path(__file__).parent / "assets/battleship.png") as img:
            cur = ImageDraw.Draw(img)

            for i, y in zip(range(1, 11), range(75, 530, 50)):
                for j, x in zip(range(1, 11), range(75, 530, 50)):
                    coord = (i, j)
                    if coord in self.op_misses:
                        self.draw_dot(cur, x, y, fill=GRAY)

                    elif coord in self.op_hits:
                        if hide:
                            self.draw_dot(cur, x, y, fill=RED)
                        else:
                            ship = self.get_ship(coord)
                            self.draw_sq(cur, x, y, coord=coord, ship=ship)
                            self.draw_dot(cur, x, y, fill=RED)

                    elif ship := self.get_ship(coord):
                        if not hide:
                            self.draw_sq(cur, x, y, coord=coord, ship=ship)
            buffer = BytesIO()
            img.save(buffer, "PNG")

        buffer.seek(0)
        del img
        return buffer


class BattleShip:
    """
    BattleShip Game
    """

    inputpat: ClassVar[re.Pattern] = re.compile(r"([a-j])(10|[1-9])")

    def __init__(
        self,
        player1: discord.User,
        player2: discord.User,
        *,
        random: bool = True,
    ) -> None:

        self.embed_color: Optional[DiscordColor] = None

        self.player1: discord.User = player1
        self.player2: discord.User = player2

        self.random: bool = random

        self.player1_board: Board = Board(player1, random=self.random)
        self.player2_board: Board = Board(player2, random=self.random)

        self.turn: discord.User = self.player1
        self.timeout: Optional[int] = None

        self.message1: Optional[discord.Message] = None
        self.message2: Optional[discord.Message] = None

    def get_board(self, player: discord.User, other: bool = False) -> Board:
        if other:
            return self.player2_board if player == self.player1 else self.player1_board
        else:
            return self.player1_board if player == self.player1 else self.player2_board

    def place_move(self, player: discord.User, coords: Coords) -> tuple[bool, bool]:
        board = self.get_board(player)
        op_board = self.get_board(player, other=True)

        for i, ship in enumerate(op_board.ships):
            for j, coord in enumerate(ship.span):
                if coords == coord:
                    op_board.ships[i].hits[j] = True
                    board.my_hits.append(coords)
                    op_board.op_hits.append(coords)
                    return all(op_board.ships[i].hits), True

        board.my_misses.append(coords)
        op_board.op_misses.append(coords)
        return False, False

    async def get_file(
        self, player: discord.User, *, hide: bool = True
    ) -> tuple[discord.Embed, discord.File, discord.Embed, discord.File]:

        board = self.get_board(player)
        image1 = await board.to_image()

        board2 = self.get_board(player, other=True)
        image2 = await board2.to_image(hide=hide)

        file1 = discord.File(image1, "board1.png")
        file2 = discord.File(image2, "board2.png")

        embed1 = discord.Embed(color=self.embed_color)
        embed2 = discord.Embed(color=self.embed_color)

        embed1.set_image(url="attachment://board1.png")
        embed2.set_image(url="attachment://board2.png")

        return embed1, file1, embed2, file2

    def to_num(self, alpha: str) -> int:
        return ord(alpha) % 96

    def get_coords(self, inp: str) -> tuple[str, Coords]:
        inp = re.sub(r"\s+", "", inp).lower()
        match = self.inputpat.match(inp)
        x, y = match.group(1), match.group(2)
        return (inp, (self.to_num(x), int(y)))

    def who_won(self) -> Optional[discord.User]:
        if self.player1_board.won():
            return self.player2
        elif self.player2_board.won():
            return self.player1
        else:
            return None

    async def get_ship_inputs(
        self, ctx: commands.Context[commands.Bot], user: discord.User
    ) -> bool:

        board = self.get_board(user)

        async def place_ship(ship: str, size: int, color: tuple[int, int, int]) -> bool:
            embed, file, _, _ = await self.get_file(user)
            await user.send(
                f"Where do you want to place your `{ship}`?\nSend the start coordinate... e.g. (`a1`)",
                embed=embed,
                file=file,
            )

            def check(msg: discord.Message) -> bool:
                if not msg.guild and msg.author == user:
                    content = re.sub(r"\s+", "", message.content).lower()
                    return bool(self.inputpat.match(content))

            try:
                message: discord.Message = await ctx.bot.wait_for(
                    "message", check=check, timeout=self.timeout
                )
            except asyncio.TimeoutError:
                await user.send(
                    f"The timeout of {self.timeout} seconds, has been reached. Aborting..."
                )
                return False

            _, start = self.get_coords(message.content)

            await user.send("Do you want it to be vertical?\nSay `yes` or `no`")

            def check(msg: discord.Message) -> bool:
                if not msg.guild and msg.author == user:
                    content = msg.content.replace(" ", "").lower()
                    return content in ("yes", "no")

            try:
                message: discord.Message = await ctx.bot.wait_for(
                    "message", check=check, timeout=self.timeout
                )
            except asyncio.TimeoutError:
                await user.send(
                    f"The timeout of {self.timeout} seconds, has been reached. Aborting..."
                )
                return False

            vertical = message.content.replace(" ", "").lower() != "yes"

            new_ship = Ship(
                name=ship,
                size=size,
                start=start,
                vertical=vertical,
                color=color,
            )

            if board._is_valid(new_ship):
                board.ships.append(new_ship)
            else:
                await user.send("That is a not a valid location, please try again")
                await place_ship(ship, size, color)

        for ship, (size, color) in SHIPS.items():
            await place_ship(ship, size, color)

        await user.send("All setup! (Game will soon start after the opponent finishes)")
        return True

    async def start(
        self, ctx: commands.Context[commands.Bot], *, timeout: Optional[float] = None
    ) -> tuple[discord.Message, discord.Message]:
        """
        starts the battleship game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        timeout : Optional[float], optional
            the timeout for when waiting, by default None

        Returns
        -------
        tuple[discord.Message, discord.Message]
            returns both player's messages respectively
        """

        await ctx.send("**Game Started!**\nI've setup the boards in your dms!")

        if not self.random:
            await asyncio.gather(
                self.get_ship_inputs(ctx, self.player1),
                self.get_ship_inputs(ctx, self.player2),
            )

        _, f1, _, f2 = await self.get_file(self.player1)
        _, f3, _, f4 = await self.get_file(self.player2)

        self.message1 = await self.player1.send("**Game starting!**", files=[f2, f1])
        self.message2 = await self.player2.send("**Game starting!**", files=[f4, f3])
        self.timeout = timeout

        while not ctx.bot.is_closed():

            def check(msg: discord.Message) -> bool:
                if not msg.guild and msg.author == self.turn:
                    content = msg.content.replace(" ", "").lower()
                    return bool(self.inputpat.match(content))

            try:
                message: discord.Message = await ctx.bot.wait_for(
                    "message", check=check, timeout=self.timeout
                )
            except asyncio.TimeoutError:
                await ctx.send(
                    f"The timeout of {timeout} seconds, has been reached. Aborting..."
                )
                break

            raw, coords = self.get_coords(message.content)

            if coords in self.get_board(self.turn):
                await self.turn.send("You've attacked this coordinate before!")

            else:
                sunk, hit = self.place_move(self.turn, coords)
                next_turn: discord.User = (
                    self.player2 if self.turn == self.player1 else self.player1
                )

                if hit and sunk:
                    await self.turn.send(
                        f"`{raw}` was a hit!, you also sank one of their ships! :)"
                    )
                    await next_turn.send(
                        f"They went for `{raw}`, and it was a hit!\nOne of your ships also got sunk! :("
                    )
                elif hit:
                    await self.turn.send(f"`{raw}` was a hit :)")
                    await next_turn.send(f"They went for `{raw}`, and it was a hit! :(")
                else:
                    await self.turn.send(f"`{raw}` was a miss :(")
                    await next_turn.send(
                        f"They went for `{raw}`, and it was a miss! :)"
                    )

                _, f1, _, f2 = await self.get_file(self.player1)
                _, f3, _, f4 = await self.get_file(self.player2)

                await self.player1.send(files=[f2, f1])
                await self.player2.send(files=[f4, f3])
                self.turn = next_turn

                if winner := self.who_won():
                    await winner.send("Congrats, you won! :)")

                    other = self.player2 if winner == self.player1 else self.player1
                    await other.send("You lost, better luck next time :(")
                    break

        return self.message1, self.message2

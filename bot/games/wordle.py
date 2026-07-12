from __future__ import annotations

import pathlib
import random
import asyncio
from typing import Optional, Final
from io import BytesIO

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from .utils import *

BORDER: Final[int] = 40
SQ: Final[int] = 100
SPACE: Final[int] = 10

WIDTH: Final[int] = BORDER * 2 + SQ * 5 + SPACE * 4
HEIGHT: Final[int] = BORDER * 2 + SQ * 6 + SPACE * 5

GRAY: Final[tuple[int, int, int]] = (119, 123, 125)
ORANGE: Final[tuple[int, int, int]] = (200, 179, 87)
GREEN: Final[tuple[int, int, int]] = (105, 169, 99)
LGRAY: Final[tuple[int, int, int]] = (198, 201, 205)


class Wordle:
    """
    Wordle Game
    """

    def __init__(self, word: Optional[str] = None, *, text_size: int = 55) -> None:
        self.embed_color: Optional[DiscordColor] = None

        parent = pathlib.Path(__file__).parent
        self._valid_words = tuple(
            open(parent / "assets/words.txt", "r").read().splitlines()
        )
        self._text_size = text_size
        self._font = ImageFont.truetype(
            str(parent / "assets/HelveticaNeuBold.ttf"), self._text_size
        )

        self.guesses: list[list[dict[str, str]]] = []

        if word:
            if len(word) != 5:
                raise ValueError("Word must be of length 5")

            if not word.isalpha():
                raise ValueError("Word must be an alphabetical string")

            self.word = word
        else:
            self.word: str = random.choice(self._valid_words)

    def parse_guess(self, guess: str) -> bool:
        self.guesses.append([])
        for ind, l in enumerate(guess):
            if l in self.word:
                color = GREEN if self.word[ind] == l else ORANGE
            else:
                color = GRAY
            self.guesses[-1].append({"letter": l, "color": color})

        return guess == self.word

    @executor()
    def render_image(self) -> BytesIO:
        with Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255)) as img:
            cursor = ImageDraw.Draw(img)

            x = y = BORDER
            for i in range(6):
                for j in range(5):
                    try:
                        letter = self.guesses[i][j]
                        color = letter["color"]
                        act_letter = letter["letter"]
                    except (IndexError, KeyError):
                        cursor.rectangle((x, y, x + SQ, y + SQ), outline=LGRAY, width=4)
                    else:
                        cursor.rectangle((x, y, x + SQ, y + SQ), width=0, fill=color)
                        cursor.text(
                            (x + SQ / 2, y + SQ / 2),
                            act_letter.upper(),
                            font=self._font,
                            anchor="mm",
                            fill=(255, 255, 255),
                        )

                    x += SQ + SPACE
                x = BORDER
                y += SQ + SPACE

            buf = BytesIO()
            img.save(buf, "PNG")
        buf.seek(0)
        return buf

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        timeout: Optional[float] = None,
        embed_color: DiscordColor = DEFAULT_COLOR,
    ) -> discord.Message:
        """
        starts the wordle game

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
        self.embed_color = discord.Color.random()

        buf = await self.render_image()

        embed = discord.Embed(title="Wordle!", color=discord.Color.random())
        embed.set_image(url="attachment://wordle.png")
        embed.set_footer(text='Say "stop" to cancel the game!')

        self.message = await ctx.send(embed=embed, file=discord.File(buf, "wordle.png"))

        while not ctx.bot.is_closed():

            def check(m: discord.Message) -> bool:
                return (
                    (len(m.content) == 5 or m.content.lower() == "stop")
                    and m.author == ctx.author
                    and m.channel == ctx.channel
                )

            try:
                guess: discord.Message = await ctx.bot.wait_for(
                    "message", timeout=timeout, check=check
                )
            except asyncio.TimeoutError:
                break

            content = guess.content.lower()

            if content == "stop":
                await ctx.send(f"Game Over! cancelled, the word was: **{self.word}**")
                break

            if content not in self._valid_words:
                await ctx.send("That is not a valid word!")
            else:
                won = self.parse_guess(content)
                buf = await self.render_image()

                await self.message.delete()

                embed = discord.Embed(title="Wordle!", color=discord.Color.random())
                embed.set_image(url="attachment://wordle.png")

                self.message = await ctx.send(
                    embed=embed, file=discord.File(buf, "wordle.png")
                )

                if won:
                    await ctx.send("Game Over! You won!")
                    break
                elif len(self.guesses) >= 6:
                    await ctx.send(
                        f"Game Over! You lose, the word was: **{self.word}**"
                    )
                    break

        return self.message

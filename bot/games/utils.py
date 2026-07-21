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

from typing import (
    Optional,
    Coroutine,
    Callable,
    Final,
    Union,
    TypeVar,
    TYPE_CHECKING,
    Any,
)

import functools
import asyncio

import discord
from discord.ext import commands
from utils.emoji import STOP_BUTTON

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, TypeAlias

    P = ParamSpec("P")
    T = TypeVar("T")

    A = TypeVar("A", bool)
    B = TypeVar("B", bool)

__all__: tuple[str, ...] = (
    "DiscordColor",
    "DEFAULT_COLOR",
    "executor",
    "chunk",
    "BaseView",
    "double_wait",
    "wait_for_delete",
)

DiscordColor: TypeAlias = Union[discord.Color, int]

DEFAULT_COLOR: Final[discord.Color] = discord.Color(0x2F3136)


def chunk(iterable: list[T], *, count: int) -> list[list[T]]:
    return [iterable[i : i + count] for i in range(0, len(iterable), count)]


def executor() -> Callable[[Callable[P, T]], Callable[P, Coroutine[Any, Any, T]]]:
    def decorator(func: Callable[P, T]) -> Callable[P, Coroutine[Any, Any, T]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            partial = functools.partial(func, *args, **kwargs)
            loop = asyncio.get_event_loop()
            return loop.run_in_executor(None, partial)

        return wrapper

    return decorator


async def wait_for_delete(
    ctx: commands.Context[commands.Bot],
    message: discord.Message,
    *,
    emoji: str = STOP_BUTTON,
    bot: Optional[discord.Client] = None,
    user: Optional[Union[discord.User, tuple[discord.User, ...]]] = None,
    timeout: Optional[float] = None,
) -> bool:

    if not user:
        user = ctx.author
    try:
        await message.add_reaction(emoji)
    except discord.DiscordException:
        pass

    def check(reaction: discord.Reaction, _user: discord.User) -> bool:
        if reaction.emoji == emoji and reaction.message == message:
            if isinstance(user, tuple):
                return _user in user
            else:
                return _user == user

    bot: discord.Client = bot or ctx.bot
    try:
        await bot.wait_for("reaction_add", timeout=timeout, check=check)
    except asyncio.TimeoutError:
        return False
    else:
        await message.delete()
        return True


async def double_wait(
    task1: Coroutine[Any, Any, A],
    task2: Coroutine[Any, Any, B],
    *,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> tuple[set[asyncio.Task[Union[A, B]]], set[asyncio.Task[Union[A, B]]],]:

    if not loop:
        loop = asyncio.get_event_loop()

    return await asyncio.wait(
        [
            loop.create_task(task1),
            loop.create_task(task2),
        ],
        return_when=asyncio.FIRST_COMPLETED,
    )


if hasattr(discord, "ui"):

    class BaseView(discord.ui.View):
        def disable_all(self) -> None:
            for button in self.children:
                if isinstance(button, discord.ui.Button):
                    button.disabled = True

        async def on_timeout(self) -> None:
            return self.stop()

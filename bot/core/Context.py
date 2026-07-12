from __future__ import annotations

from discord.ext import commands
import discord
import functools
from typing import Optional, Any
import asyncio

__all__ = ("Context", )


class Context(commands.Context):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "<core.Context>"

    @property
    async def session(self):
        return self.bot.session

    @discord.utils.cached_property
    def replied_reference(self) -> Optional[discord.Message]:
        ref = self.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved.to_reference()
        return None

    def with_type(func):

        @functools.wraps(func)
        async def wrapped(self, *args, **kwargs):
            context = args[0] if isinstance(args[0],
                                            commands.Context) else args[1]
            try:
                async with context.typing():
                    await func(*args, **kwargs)
            except discord.Forbidden:  
                await func(*args, **kwargs)

        return wrapped

    async def show_help(self, command: str = None) -> Any:
        cmd = self.bot.get_command('help')
        command = command or self.command.qualified_name
        await self.invoke(cmd, command=command)

    async def send(self,
                   content: Optional[str] = None,
                   **kwargs) -> Optional[discord.Message]:
        if not (self.channel.permissions_for(self.me)).send_messages:
            try:
                await self.author.send(
                    "bot dont have perms to send msg in that channel")
            except discord.Forbidden:  
                pass
            return
        return await super().send(content, **kwargs)

    async def reply(self,
                    content: Optional[str] = None,
                    **kwargs) -> Optional[discord.Message]:
        if not (self.channel.permissions_for(self.me)).send_messages:
            try:
                await self.author.send(
                    "bot dont have perms to send msg in that channel")
            except discord.Forbidden:  
                pass
            return
        return await super().reply(content, **kwargs)

    async def release(self, delay: Optional[int] = None) -> None:
        delay = delay or 0
        await asyncio.sleep(delay)

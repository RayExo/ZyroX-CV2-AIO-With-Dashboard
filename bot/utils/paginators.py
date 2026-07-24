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
import os 
import discord
from utils.config import BotName
from discord.ext import commands
try:
    from discord.ext import menus
except ModuleNotFoundError as e:
    # SECURITY (audit C8/H2): do NOT auto-install from a mutable git branch at
    # import time. discord-ext-menus is a declared dependency (requirements.txt);
    # if it's missing, fail loudly so the operator installs a pinned version.
    raise ImportError(
        "discord-ext-menus is required. Install it with: pip install discord-ext-menus"
    ) from e

from .paginator import Paginator as EmbedPaginator
from discord.ext.commands import Context, Paginator as CmdPaginator
from typing import Any, List


class FieldPagePaginator(menus.ListPageSource):

    def __init__(self,
                 entries: list[tuple[Any, Any]],
                 *,
                 per_page: int = 10,
                 inline: bool = False,
                 **kwargs) -> None:
        super().__init__(entries, per_page=per_page)
        self.embed: discord.Embed = discord.Embed(
            title=kwargs.get('title'),
            description=kwargs.get('description'),
            color=0xFF0000)
        self.inline: bool = inline

    async def format_page(self, menu: EmbedPaginator,
                          entries: list[tuple[Any, Any]]) -> discord.Embed:
        self.embed.clear_fields()

        for key, value in entries:
            self.embed.add_field(name=key, value=value, inline=self.inline)

        maximum = self.get_max_pages()
        if maximum > 1:
            text = f'• Page {menu.current_page + 1}/{maximum} | Requested by {menu.ctx.author.display_name}'
            self.embed.set_footer(
                text=text,
                icon_url=
                "https://cdn.discordapp.com/icons/699587669059174461/f689b4366447d5a23eda8d0ec749c1ba.png?width=115&height=115"
            )
            #self.embed.timestamp = discord.utils.utcnow()
        return self.embed


class TextPaginator(menus.ListPageSource):

    def __init__(self, text, *, prefix='```', suffix='```', max_size=2000):
        pages = CmdPaginator(prefix=prefix,
                             suffix=suffix,
                             max_size=max_size - 200)
        for line in text.split('\n'):
            pages.add_line(line)

        super().__init__(entries=pages.pages, per_page=1)

    async def format_page(self, menu, content):
        maximum = self.get_max_pages()
        if maximum > 1:
            return f'{content} {BotName} • Page {menu.current_page + 1}/{maximum}'
        return content


class DescriptionEmbedPaginator(menus.ListPageSource):

    def __init__(self,
                 entries: list[Any],
                 *,
                 per_page: int = 10,
                 **kwargs) -> None:
        super().__init__(entries, per_page=per_page)
        self.embed: discord.Embed = discord.Embed(
            title=kwargs.get('title'),
            color=0xFF0000,
        )

    async def format_page(self, menu: EmbedPaginator,
                          entries: list[tuple[Any, Any]]) -> discord.Embed:
        self.embed.clear_fields()

        self.embed.description = '\n'.join(entries)
        #self.embed.timestamp = discord.utils.utcnow()
        maximum = self.get_max_pages()
        if maximum > 1:
            text = f'• Page {menu.current_page + 1}/{maximum} | Requested by {menu.ctx.author.display_name}'
            self.embed.set_footer(
                text=text,
                icon_url=
                "https://cdn.discordapp.com/icons/699587669059174461/f689b4366447d5a23eda8d0ec749c1ba.png?width=115&height=115"
            )

        return self.embed

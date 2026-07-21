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

"""
Shared CV2 (Component V2) utilities for the bot.
Provides a helper to build Container objects since Container()
does NOT accept positional children arguments — items must be
added via .add_item().
"""

import discord
from discord.ui import LayoutView, TextDisplay, Separator, Container


def build_container(*items, accent_color=None):
    """Build a Container and add items to it via .add_item()."""
    container = Container(accent_color=accent_color)
    for item in items:
        container.add_item(item)
    return container


class CV2(LayoutView):
    """Quick helper: CV2("Title", "section1", "section2", ...)"""
    def __init__(self, title, *sections):
        super().__init__(timeout=None)
        container = build_container(
            TextDisplay(f"**{title}**"),
            *[item for s in sections for item in (Separator(visible=True), TextDisplay(str(s)))]
        )
        self.add_item(container)

def add_action_rows(container, components):
    """Safely adds components to a CV2 container across multiple ActionRows"""
    from discord.ui import ActionRow
    current_row = []
    for item in components:
        if getattr(item, 'type', None) and getattr(item.type, 'value', 0) != 2:
            if current_row:
                container.add_item(ActionRow(*current_row))
                current_row = []
            container.add_item(ActionRow(item))
        else:
            current_row.append(item)
            if len(current_row) == 5:
                container.add_item(ActionRow(*current_row))
                current_row = []
    if current_row:
        container.add_item(ActionRow(*current_row))

class CV2Embed(CV2):
    """A CV2 container that behaves like a discord.Embed."""
    def __init__(self, title="", description="", **kwargs):
        self._title = title
        self._description = description or ""
        self._fields = []
        self._footer = None
        super().__init__(title, self._description)
        self.color = kwargs.get("color", 0xFF0000)
    
    def _rebuild(self):
        self.clear_items()
        sections = [self._description] if self._description else []
        for name, value in self._fields:
            sections.append(f"**{name}**\n{value}")
        
        if self._footer:
            sections.append(f"*{self._footer}*")
            
        container = build_container(
            TextDisplay(f"**{self._title}**"),
            *[item for s in sections for item in (Separator(visible=True), TextDisplay(str(s)))]
        )
        self.add_item(container)

    def add_field(self, name, value, inline=False, **kwargs):
        self._fields.append((name, value))
        self._rebuild()
        return self

    def set_footer(self, text=None, icon_url=None, **kwargs):
        if text:
            self._footer = text
            self._rebuild()
        return self
        
    def set_thumbnail(self, url=None, **kwargs):
        return self
        
    def set_author(self, name=None, url=None, icon_url=None, **kwargs):
        return self
        
    def set_image(self, url=None, **kwargs):
        return self
        
    def to_dict(self):
        return {"title": self._title, "description": self._description}

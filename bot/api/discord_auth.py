# ╔══════════════════════════════════════════════════════════════════╗
# ║  Discord OAuth permission checks for dashboard API requests      ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import re
from typing import Any

import aiohttp
from fastapi import HTTPException, Request

from utils.config import OWNER_IDS_STR

MANAGE_GUILD = 0x20
ADMINISTRATOR = 0x8

GUILD_PATH_RE = re.compile(r"^/api/v1/guilds/(\d+)(?:/|$)")


def _parse_admin_ids() -> list[str]:
    import os

    raw = os.getenv("DASHBOARD_ADMIN_IDS", "").strip()
    if raw:
        return [p.strip() for p in raw.split(",") if p.strip().isdigit()]
    return list(OWNER_IDS_STR)


def can_manage_guild(guild: dict[str, Any]) -> bool:
    if guild.get("owner"):
        return True
    try:
        perms = int(guild.get("permissions", "0"))
    except (TypeError, ValueError):
        return False
    return bool(perms & ADMINISTRATOR) or bool(perms & MANAGE_GUILD)


async def fetch_user_guilds(access_token: str) -> list[dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://discord.com/api/users/@me/guilds",
            headers={"Authorization": f"Bearer {access_token}"},
        ) as resp:
            if resp.status != 200:
                raise HTTPException(
                    status_code=403,
                    detail="Invalid or expired Discord access token.",
                )
            data = await resp.json()
            return data if isinstance(data, list) else []


async def verify_discord_token(access_token: str) -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        ) as resp:
            if resp.status != 200:
                raise HTTPException(
                    status_code=403,
                    detail="Invalid or expired Discord access token.",
                )
            return await resp.json()


async def user_can_manage_guild(access_token: str, guild_id: int) -> bool:
    guilds = await fetch_user_guilds(access_token)
    for guild in guilds:
        if str(guild.get("id")) == str(guild_id):
            return can_manage_guild(guild)
    return False


async def get_manageable_guild_ids(access_token: str) -> set[str]:
    guilds = await fetch_user_guilds(access_token)
    return {str(g["id"]) for g in guilds if can_manage_guild(g)}


def get_discord_headers(request: Request) -> tuple[str | None, str | None]:
    token = request.headers.get("X-Discord-Access-Token")
    user_id = request.headers.get("X-Discord-User-Id")
    return token, user_id


async def require_discord_session(request: Request) -> tuple[str, str]:
    token, user_id = get_discord_headers(request)
    if not token:
        raise HTTPException(
            status_code=403,
            detail="X-Discord-Access-Token header is required.",
        )

    user = await verify_discord_token(token)
    resolved_id = str(user.get("id", ""))
    if not resolved_id:
        raise HTTPException(status_code=403, detail="Could not resolve Discord user.")

    if user_id and user_id != resolved_id:
        raise HTTPException(status_code=403, detail="Discord user ID mismatch.")

    return token, resolved_id


async def require_guild_access(request: Request, guild_id: int) -> None:
    token, _ = await require_discord_session(request)
    if not await user_can_manage_guild(token, guild_id):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to manage this guild.",
        )


async def require_dashboard_admin(request: Request) -> None:
    token, user_id = await require_discord_session(request)
    admin_ids = _parse_admin_ids()
    if user_id not in admin_ids:
        raise HTTPException(
            status_code=403,
            detail="Dashboard admin access required.",
        )


def extract_guild_id_from_path(path: str) -> int | None:
    match = GUILD_PATH_RE.match(path)
    if not match:
        return None
    return int(match.group(1))

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
Application Emoji Sync Utility
Reads all custom Discord emojis from utils/emoji.py, checks them against
the bot's application emojis, uploads any that are missing, and patches
emoji.py in-place with corrected IDs.

Controlled by EMOJI_SYNC in .env:
  EMOJI_SYNC="true"   → runs on every startup
  EMOJI_SYNC="false"  → skipped entirely

If emoji.py is patched (new uploads or ID fixes), the bot automatically
restarts so the fresh IDs are loaded into memory.

Call `run_sync(token)` once inside on_ready.
"""

import os
import re
import sys
import base64
import asyncio
import aiohttp
from colorama import Fore, Style, init

init(autoreset=True)

EMOJI_PY_PATH = os.path.join(os.path.dirname(__file__), "emoji.py")


def _log(level: str, color: str, symbol: str, msg: str) -> None:
    print(f"{color}{symbol} {level}:{Style.RESET_ALL} {msg}")

def info(msg):    _log("EmojiSync", Fore.CYAN,    "◈", msg)
def success(msg): _log("EmojiSync", Fore.GREEN,   "✔", msg)
def warning(msg): _log("EmojiSync", Fore.YELLOW,  "↻", msg)
def error(msg):   _log("EmojiSync", Fore.RED,     "✖", msg)
def system(msg):  _log("EmojiSync", Fore.MAGENTA, "★", msg)


def _restart() -> None:
    """Replace the current process with a fresh copy of itself."""
    system(f"Restarting bot to load updated emoji IDs...")
    # Flush stdout so the message is visible before the process is replaced
    sys.stdout.flush()
    os.execv(sys.executable, [sys.executable] + sys.argv)


async def _fetch_emoji_image(session: aiohttp.ClientSession, emoji_id: str, animated: bool):
    ext = "gif" if animated else "webp"
    url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
    try:
        async with session.get(url, allow_redirects=True) as r:
            if r.status == 200:
                return await r.read()
    except Exception:
        pass
    return None


async def run_sync(token: str) -> None:
    """
    Async emoji sync. Pass the bot token directly.
    Respects the EMOJI_SYNC env var — set to "false" to disable.
    Triggers an automatic restart when emoji.py is patched.
    """
    # ── Toggle check ──────────────────────────────────────────────────────────
    enabled = os.getenv("EMOJI_SYNC", "true").strip().lower()
    if enabled != "true":
        info(f"Disabled via EMOJI_SYNC={enabled!r} — skipping.")
        return

    if not token:
        warning("No token provided — skipping EmojiSync.")
        return

    # ── Read emoji.py ─────────────────────────────────────────────────────────
    try:
        with open(EMOJI_PY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as err:
        error(f"Could not read emoji.py ({err})")
        return

    matches = set(re.findall(r"<(a?):(\w+):(\d+)>", content))
    if not matches:
        info("No custom emojis found in emoji.py — nothing to sync.")
        return

    system(f"Starting Application Emoji Sync — {len(matches)} unique emojis found in emoji.py")

    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        # Fetch bot application ID
        async with session.get("https://discord.com/api/v10/users/@me") as r:
            if r.status != 200:
                error(f"Failed to fetch bot info [HTTP {r.status}]")
                return
            app_id = (await r.json()).get("id")

        # Fetch existing application emojis
        async with session.get(f"https://discord.com/api/v10/applications/{app_id}/emojis") as r:
            if r.status != 200:
                error(f"Failed to fetch application emojis [HTTP {r.status}]")
                return
            data = await r.json()
            app_emojis: list = data.get("items", []) if isinstance(data, dict) else data

        info(
            f"Found {Fore.YELLOW}{len(matches)}{Style.RESET_ALL} templates "
            f"{Fore.LIGHTBLACK_EX}|{Style.RESET_ALL} "
            f"Application hosts {Fore.GREEN}{len(app_emojis)}{Style.RESET_ALL} emojis"
        )

        updated = False
        skipped = uploaded = fixed = failed = 0

        for animated_str, name, old_id in matches:
            animated = animated_str == "a"

            existing = (
                next((e for e in app_emojis if e["id"] == old_id), None)
                or next((e for e in app_emojis if e["name"] == name), None)
            )

            if existing:
                new_id = existing["id"]
                if old_id != new_id:
                    old_str = f"<{animated_str}:{name}:{old_id}>"
                    new_str = f"<{animated_str}:{existing['name']}:{new_id}>"
                    content = content.replace(old_str, new_str)
                    updated = True
                    fixed += 1
                    warning(f"Auto-fixing ID: {name} {Fore.LIGHTBLACK_EX}-> {new_id}")
                else:
                    skipped += 1
                continue

            # Not found — upload it
            info(f"Uploading: {name} {Fore.LIGHTBLACK_EX}(not in application emojis)")

            image_data = await _fetch_emoji_image(session, old_id, animated)
            if not image_data:
                error(f"Could not download image for {name} [ID: {old_id}]")
                failed += 1
                continue

            mime = "image/gif" if animated else "image/webp"
            b64 = base64.b64encode(image_data).decode("utf-8")
            image_uri = f"data:{mime};base64,{b64}"

            async with session.post(
                f"https://discord.com/api/v10/applications/{app_id}/emojis",
                json={"name": name, "image": image_uri},
            ) as r2:
                if r2.status in (200, 201):
                    new_emoji = await r2.json()
                    new_id = new_emoji["id"]
                    old_str = f"<{animated_str}:{name}:{old_id}>"
                    new_str = f"<{animated_str}:{new_emoji['name']}:{new_id}>"
                    content = content.replace(old_str, new_str)
                    app_emojis.append(new_emoji)
                    updated = True
                    uploaded += 1
                    success(f"Uploaded: {name} {Fore.LIGHTBLACK_EX}[saved as ID: {new_id}]")
                else:
                    resp_text = await r2.text()
                    error(f"Discord rejected {name} -> {resp_text}")
                    failed += 1

            # Small delay to respect Discord rate limits
            await asyncio.sleep(0.5)

    # ── Write patched emoji.py ────────────────────────────────────────────────
    if updated:
        try:
            with open(EMOJI_PY_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            success("emoji.py patched in-place to reflect current API state.")
        except Exception as err:
            error(f"Could not write patched emoji.py ({err})")
            updated = False  # don't restart if we couldn't save

    # ── Summary ───────────────────────────────────────────────────────────────
    parts = []
    if skipped:  parts.append(f"{Fore.GREEN}{skipped} already matching{Style.RESET_ALL}")
    if fixed:    parts.append(f"{Fore.YELLOW}{fixed} ID mismatches fixed{Style.RESET_ALL}")
    if uploaded: parts.append(f"{Fore.CYAN}{uploaded} newly uploaded{Style.RESET_ALL}")
    if failed:   parts.append(f"{Fore.RED}{failed} failures{Style.RESET_ALL}")

    if parts:
        system("Sync complete: " + f" {Fore.LIGHTBLACK_EX}|{Style.RESET_ALL} ".join(parts))
    else:
        system("Sync complete: nothing to do.")

    # ── Auto-restart if emoji.py was changed ─────────────────────────────────
    if updated:
        _restart()

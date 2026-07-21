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

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN      = os.environ.get("TOKEN")
BRAND_NAME = os.environ.get("brand_name", "Zyrox X")
NAME       = BRAND_NAME
BotName    = BRAND_NAME

server     = "https://discord.gg/codexdev"
serverLink = "https://discord.gg/codexdev"
ch         = "https://discord.com/channels/699587669059174461/1271825678710476911"

# ── Security / feature toggles ────────────────────────────────────────────────

def _env_bool(key: str, default: bool = False) -> bool:
    raw = os.getenv(key, str(default)).strip().lower()
    return raw in ("1", "true", "yes", "on")


JISHAKU_ENABLED = _env_bool("JISHAKU_ENABLED", False)
API_ENABLED = _env_bool("API_ENABLED", False)
TUNNEL_ENABLED = _env_bool("TUNNEL_ENABLED", False)
TUNNEL_ALLOW_BINARY_DOWNLOAD = _env_bool("TUNNEL_ALLOW_BINARY_DOWNLOAD", False)

API_HOST = os.getenv("API_HOST", "127.0.0.1").strip() or "127.0.0.1"
API_PORT = int(os.getenv("API_PORT", "8000"))

# ── Webhooks (only active when explicitly configured) ─────────────────────────

def _valid_webhook_url(url: str | None) -> str | None:
    if not url:
        return None
    url = url.strip()
    if not url or url == "https://discord.com/api/webhooks/":
        return None
    if "discord.com/api/webhooks/" not in url and "discordapp.com/api/webhooks/" not in url:
        return None
    return url

CMD_WEBHOOK_URL = _valid_webhook_url(os.getenv("CMD_WEBHOOK_URL"))

# ── Optional Discord log / stats channels (unset = disabled) ──────────────────

def _parse_optional_id(env_key: str) -> int | None:
    raw = os.getenv(env_key, "").strip()
    if not raw or not raw.isdigit():
        return None
    return int(raw)

LOG_CHANNEL_ID = _parse_optional_id("LOG_CHANNEL_ID")
SERVER_COUNT_CHANNEL_ID = _parse_optional_id("SERVER_COUNT_CHANNEL_ID")
USER_COUNT_CHANNEL_ID = _parse_optional_id("USER_COUNT_CHANNEL_ID")

# ── Owner / Staff IDs ─────────────────────────────────────────────────────────
# REQUIRED: set OWNER_IDS in .env — no hardcoded fallback IDs.

def _parse_ids(env_key: str) -> list[int]:
    raw = os.getenv(env_key, "").strip()
    if not raw:
        return []
    return [int(p.strip()) for p in raw.split(",") if p.strip().isdigit()]

OWNER_IDS:     list[int] = _parse_ids("OWNER_IDS")
OWNER_IDS_STR: list[str] = [str(i) for i in OWNER_IDS]

# Aliases kept for backwards compatibility with files that import these names
BOT_OWNER_IDS     = OWNER_IDS
BOT_OWNER_IDS_STR = OWNER_IDS_STR
STAFF_IDS         = OWNER_IDS
STAFF_IDS_STR     = OWNER_IDS_STR

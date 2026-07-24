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

CMD_WEBHOOK_URL = os.getenv("CMD_WEBHOOK_URL")

# ── Owner / Staff IDs ─────────────────────────────────────────────────────────
# Edit OWNER_IDS in .env — comma-separated, no spaces needed.
# Example:  OWNER_IDS = 111111111111111111,222222222222222222

# Known insecure default values shipped in .env.example — the bot refuses to
# start while any critical secret is still set to one of these.
_INSECURE_DEFAULTS = {
    "ZYROX_SECURE_API_KEY_12345_CHANGE_THIS_ASAP_BY_CODEX_DEVS",
    "zyrox_nextauth_default_secret_string_2026_change_me_BY_CODEX_DEVS",
    "TOKEN_HERE",
    "youshallnotpass",
}


def _parse_ids(env_key: str, defaults: list[int]) -> list[int]:
    raw = os.getenv(env_key, "").strip()
    if not raw:
        return defaults
    ids = [int(p.strip()) for p in raw.split(",") if p.strip().isdigit()]
    return ids or defaults


def _parse_ids_required(env_key: str) -> list[int]:
    """Parse a REQUIRED comma-separated list of Discord user IDs.

    SECURITY: unlike _parse_ids, this NEVER falls back to a hardcoded default.
    A missing/invalid value raises at import time, so a deployment cannot
    silently inherit the original author's owner privileges (audit finding H12).
    """
    raw = os.getenv(env_key, "").strip()
    if not raw:
        raise RuntimeError(
            f"[security] {env_key} must be set in your .env file "
            f"(comma-separated Discord user IDs). The bot will not start without it."
        )
    ids = [int(p.strip()) for p in raw.split(",") if p.strip().isdigit()]
    if not ids:
        raise RuntimeError(
            f"[security] {env_key} is set but contains no valid numeric Discord user IDs."
        )
    return ids


def validate_critical_secrets() -> None:
    """Fail fast at startup if critical secrets are missing or still defaults.

    Call this once from the bot entrypoint (CodeX.py) during startup.
    Closes audit findings C2 (default secrets) and H12 (OWNER_IDS backdoor).
    """
    token = (os.getenv("TOKEN") or "").strip()
    if not token or token in _INSECURE_DEFAULTS:
        raise RuntimeError("[security] TOKEN is missing or still a placeholder. Set it in .env.")

    if os.environ.get("API_ENABLED", "false").lower() == "true":
        key = (os.getenv("DASHBOARD_API_KEY") or "").strip()
        if not key or key in _INSECURE_DEFAULTS or len(key) < 32:
            raise RuntimeError(
                "[security] DASHBOARD_API_KEY is missing, shorter than 32 characters, "
                'or still a shipped default. Generate one with: '
                'python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )


OWNER_IDS:     list[int] = _parse_ids_required("OWNER_IDS")
OWNER_IDS_STR: list[str] = [str(i) for i in OWNER_IDS]

# Aliases kept for backwards compatibility with files that import these names
BOT_OWNER_IDS     = OWNER_IDS
BOT_OWNER_IDS_STR = OWNER_IDS_STR
STAFF_IDS         = OWNER_IDS
STAFF_IDS_STR     = OWNER_IDS_STR
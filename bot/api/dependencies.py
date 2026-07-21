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
from typing import Optional, TYPE_CHECKING
from fastapi import HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from slowapi import Limiter
from slowapi.util import get_remote_address

if TYPE_CHECKING:
    from core.zyrox import zyrox

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["1000 per minute"])

# Global reference to the bot instance
_bot_instance: Optional["zyrox"] = None

# Security scheme
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Dependency to verify the API key from the Authorization header.
    Expected: Authorization: Bearer <API_KEY>
    """
    api_key = os.getenv("DASHBOARD_API_KEY")
    
    # If no key is set in env, we might want to allow for local testing or force it.
    # The requirement says "Read API key from environment variable", implying it's required.
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="DASHBOARD_API_KEY environment variable is not set."
        )

    if credentials.credentials != api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key."
        )
    return credentials.credentials

def set_bot(bot_instance: "zyrox"):
    """
    Sets the global bot instance. 
    This should be called in CodeX.py during startup.
    """
    global _bot_instance
    _bot_instance = bot_instance

def get_bot() -> "zyrox":
    """
    FastAPI dependency to retrieve the Discord bot instance.
    Usage: bot: zyrox = Depends(get_bot)
    """
    if _bot_instance is None:
        raise HTTPException(
            status_code=503, 
            detail="Discord bot instance is not initialized yet."
        )
    return _bot_instance

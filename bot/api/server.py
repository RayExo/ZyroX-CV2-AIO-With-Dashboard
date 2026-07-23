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

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import time
import json
import logging
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from utils.config import *


from api.routes import bot, guilds, admin
from api.dependencies import verify_api_key, limiter
from api.db_manager import db_manager
from api.discord_auth import (
    require_dashboard_admin,
    require_discord_session,
    require_guild_access,
    extract_guild_id_from_path,
)
from fastapi.responses import JSONResponse

# Configure logging
logger = logging.getLogger("api_request_logs")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup: Nothing special needed for now
    yield
    # Shutdown: Close all shared database connections
    await db_manager.close_all()

def create_app() -> FastAPI:
    """
    Initializes the FastAPI application for the CodeX Bot Dashboard.
    The bot instance will be attached to app.state.bot in CodeX.py at runtime.
    """
    app = FastAPI(
        title=f"{BRAND_NAME} Bot API",
        description=f"REST API to manage the {BRAND_NAME} Discord Bot features",
        version="1.0",
        dependencies=[Depends(verify_api_key)],
        lifespan=lifespan
    )

    # Discord permission checks for dashboard API routes
    @app.middleware("http")
    async def discord_permission_middleware(request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        try:
            if path.startswith("/api/v1/admin"):
                await require_dashboard_admin(request)
            elif path.startswith("/api/v1/bot"):
                await require_discord_session(request)
            elif path.startswith("/api/v1/guilds"):
                guild_id = extract_guild_id_from_path(path)
                if guild_id is not None:
                    await require_guild_access(request, guild_id)
                else:
                    await require_discord_session(request)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        return await call_next(request)

    # Structured Logging Middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        log_data = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(process_time * 1000, 2),
            "client_ip": request.client.host if request.client else "unknown"
        }
        
        logger.info(json.dumps(log_data))
        return response

    # Attach limiter and handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # Build allowed origins from env + hardcoded fallbacks
    _extra_origins = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "").split(",")
        if o.strip()
    ]
    _allowed_origins = list(dict.fromkeys([
        "http://localhost:3000",
        "https://localhost:3000",
        "https://your-vercel-url-here.vercel.app",
        *_extra_origins,
    ]))

    # Enable CORS for Next.js dashboard
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(bot.router, prefix="/api/v1/bot", tags=["Bot"])
    app.include_router(guilds.router, prefix="/api/v1/guilds", tags=["Guilds"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

    @app.get("/", summary="API Root", description="Returns basic API information and online status.")
    async def root():
        return {
            "status": "online",
            "bot_name": {BRAND_NAME},
            "api_version": "1.0"
        }

    @app.get("/health", summary="Health Check", description="Performs a health check for container orchestration and uptime monitoring.")
    async def health():
        return {"status": "ok"}

    return app

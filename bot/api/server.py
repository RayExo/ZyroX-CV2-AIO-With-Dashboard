from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
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

    # Enable CORS for Next.js dashboard
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://localhost:3000",
            # Add production domain here later
        ],
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

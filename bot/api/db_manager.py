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

import aiosqlite
import asyncio
from typing import Dict

class DatabaseManager:
    """
    A simple manager for persistent SQLite connections to avoid 
    opening/closing files on every API request.
    """
    def __init__(self):
        self._connections: Dict[str, aiosqlite.Connection] = {}
        self._lock = asyncio.Lock()

    async def get_connection(self, db_path: str) -> aiosqlite.Connection:
        """
        Retrieves an existing connection or creates a new one for the given path.
        """
        async with self._lock:
            if db_path not in self._connections:
                # We use check_same_thread=False because aiosqlite handles 
                # thread safety by running queries in a dedicated thread.
                conn = await aiosqlite.connect(db_path, check_same_thread=False)
                conn.row_factory = aiosqlite.Row
                self._connections[db_path] = conn
            return self._connections[db_path]

    async def close_all(self):
        """
        Closes all open connections. Called on API shutdown.
        """
        async with self._lock:
            for path, conn in self._connections.items():
                try:
                    await conn.close()
                except:
                    pass
            self._connections.clear()

# Singleton instance
db_manager = DatabaseManager()

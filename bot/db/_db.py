import aiosqlite
import asyncio
import random
from typing import Optional

class Database:
    _instance: Optional['Database'] = None
    _lock: asyncio.Lock
    db_path: str
    db: Optional[aiosqlite.Connection]

    def __new__(cls, db_path='db/anti.db'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_path = db_path
            cls._instance.db = None
            cls._instance._lock = asyncio.Lock()
        return cls._instance

    async def connect(self, timeout=30):
        async with self._lock:
            if self.db is None:
                self.db = await aiosqlite.connect(self.db_path, timeout=timeout)
                await self.db.execute('PRAGMA journal_mode=WAL;')
                await self.db.commit()
        return self.db

    async def ensure_connection(self):
        if self.db is None or not self.db.is_open:
            await self.connect()
        return self.db

    async def execute_with_retries(self, func, retries=5, delay=1):
        for attempt in range(retries):
            try:
                return await func()
            except aiosqlite.OperationalError as e:
                if 'database is locked' in str(e).lower():
                    sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Database is locked. Retryng in {sleep_time:.2f} seconds.....")
                    await asyncio.sleep(sleep_time)
                else:
                    raise
        raise Exception("Max retrys.")

    async def close(self):
        async with self._lock:
            if self.db is not None:
                await self.db.close()
                self.db = None
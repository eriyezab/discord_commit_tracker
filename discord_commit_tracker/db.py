from __future__ import annotations

import aiosqlite


class Database:
    def __init__(self, path: str) -> None:
        self._path = path
        self._conn: aiosqlite.Connection | None = None

    async def init(self) -> None:
        self._conn = await aiosqlite.connect(self._path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tracked_repos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name       TEXT NOT NULL UNIQUE,
                webhook_secret  TEXT NOT NULL,
                added_at        TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def add_repo(self, full_name: str, webhook_secret: str) -> None:
        assert self._conn is not None
        await self._conn.execute(
            "INSERT INTO tracked_repos (full_name, webhook_secret) VALUES (?, ?)",
            (full_name, webhook_secret),
        )
        await self._conn.commit()

    async def remove_repo(self, full_name: str) -> None:
        assert self._conn is not None
        await self._conn.execute(
            "DELETE FROM tracked_repos WHERE full_name = ?",
            (full_name,),
        )
        await self._conn.commit()

    async def get_repo(self, full_name: str) -> aiosqlite.Row | None:
        assert self._conn is not None
        async with self._conn.execute(
            "SELECT * FROM tracked_repos WHERE full_name = ?",
            (full_name,),
        ) as cursor:
            return await cursor.fetchone()

    async def list_repos(self) -> list[aiosqlite.Row]:
        assert self._conn is not None
        async with self._conn.execute("SELECT * FROM tracked_repos ORDER BY added_at") as cursor:
            return await cursor.fetchall()

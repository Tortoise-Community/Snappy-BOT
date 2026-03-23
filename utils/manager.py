from datetime import datetime, timedelta
import asyncpg


class Database:

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.dsn)

    async def close(self):
        if self.pool:
            await self.pool.close()


class PointsManager:
    def __init__(self, db: Database):
        self.db = db

    async def setup(self):
        await self.db.pool.execute(
            """
            CREATE TABLE IF NOT EXISTS points (
                guild_id BIGINT NOT NULL,
                user_id  BIGINT NOT NULL,
                points   INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )

    async def add_points(self, guild_id: int, user_id: int, amount: int) -> int:
        row = await self.db.pool.fetchrow(
            """
            INSERT INTO points (guild_id, user_id, points)
            VALUES ($1, $2, $3)
            ON CONFLICT (guild_id, user_id)
            DO UPDATE SET points = points.points + EXCLUDED.points
            RETURNING points
            """,
            guild_id,
            user_id,
            amount,
        )
        return row["points"]

    async def remove_points(self, guild_id: int, user_id: int, amount: int) -> int:
        row = await self.db.pool.fetchrow(
            """
            INSERT INTO points (guild_id, user_id, points)
            VALUES ($1, $2, 0)
            ON CONFLICT (guild_id, user_id)
            DO UPDATE
            SET points = GREATEST(points.points - $3, 0)
            RETURNING points
            """,
            guild_id,
            user_id,
            amount,
        )
        return row["points"]

    async def get_points(self, guild_id: int, user_id: int) -> int:
        return (
            await self.db.pool.fetchval(
                "SELECT points FROM points WHERE guild_id = $1 AND user_id = $2",
                guild_id,
                user_id,
            )
            or 0
        )

    async def get_leaderboard(
        self, guild_id: int, min_points: int = 1, limit: int = 10
    ):
        rows = await self.db.pool.fetch(
            """
            SELECT user_id, points
            FROM points
            WHERE guild_id = $1 AND points >= $2
            ORDER BY points DESC
            LIMIT $3
            """,
            guild_id,
            min_points,
            limit,
        )
        return [(r["user_id"], r["points"]) for r in rows]

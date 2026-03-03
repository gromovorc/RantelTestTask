import json
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.db.tables import tickets_table

CACHE_KEY = "dashboard:ticket_counts"

class DashboardService:
    def __init__(self, session: AsyncSession, redis:Redis):
        self._session = session
        self._redis = redis

    async def get_ticket_counts(self) -> dict:

        cached = await self._redis.get(CACHE_KEY)

        if cached:
            return json.loads(cached)

        select_stmt = sa.select(tickets_table.c.status, sa.func.count()).group_by(tickets_table.c.status)

        result = await self._session.execute(select_stmt)

        rows = result.all()

        counts = {
            "new": 0,
            "in_progress": 0,
            "waiting": 0,
            "resolved": 0,
            "closed": 0,
        }

        for status, count in rows:
            counts[status] = count

        await self._redis.set(
            CACHE_KEY,
            json.dumps(counts),
            ex=60
        )

        return counts
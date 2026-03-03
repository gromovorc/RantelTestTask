import asyncio
import contextlib
from collections.abc import AsyncIterator
import sqlalchemy as sa
import logging

from aiohttp import web

from app.db.database import async_session_maker
from app.db.tables import tickets_table
from app.services.tickets import TicketsService
from app.services.dashboard import CACHE_KEY

logger = logging.getLogger(__name__)

async def close_tickets_in_waiting(app: web.Application) -> AsyncIterator[None]:
    logger.info("background closer for tickets started")
    while True:
        try:
            async with async_session_maker() as session:
                limit = sa.func.now() - sa.text("interval '24 hours'")

                close_stmt = (
                    sa.select(tickets_table.c.id)
                    .where(
                        tickets_table.c.status == "waiting",
                        tickets_table.c.status_last_updated < limit
                    )
                    .limit(100)
                )

                result = await session.execute(close_stmt)
                rows = [row[0] for row in result.all()]

                if rows:
                    service = TicketsService(session)
                    closed = 0
                    for ticket_id in rows:
                        updated = await service.update_ticket(
                            ticket_id=ticket_id,
                            status="closed",
                            priority=None,
                            subject=None,
                            operator_id=None,
                            client_id=None,
                        )
                        if updated:
                            closed += 1

                        logger.info("closer: % closing % ticket", closed, ticket_id)

                        r = app.get("redis")
                        if r:
                            await r.delete(CACHE_KEY)

        except asyncio.CancelledError:
            logger.info("background closer for tickets done")
            raise

        except Exception:
            logger.exception("background closer for tickets exception")
        await asyncio.sleep(60)

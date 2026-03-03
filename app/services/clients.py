from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from app.db.tables import clients_table

class ClientsService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_client(self, name: str, email: str) -> dict:

        insert_stmt = pg_insert(clients_table).values(
            name=name,
            email=email
        ).returning(
            clients_table.c.id,
            clients_table.c.name,
            clients_table.c.email
        )

        result = await self._session.execute(insert_stmt)

        await self._session.commit()

        return dict(result.mappings().one())

    async def get_client(self, client_id: int) -> dict | None:

        select_stmt = sa.select(
            clients_table.c.id,
            clients_table.c.name,
            clients_table.c.email,
        ).where(clients_table.c.id == client_id)

        rows = await self._session.execute(select_stmt)

        row = rows.mappings().one_or_none()

        return dict(row) if row else None

    async def get_clients_list(self, limit: int = 20, offset: int = 0) -> list[dict]:
        select_stmt = sa.select(
            clients_table.c.id,
            clients_table.c.name,
            clients_table.c.email,
        ).order_by(clients_table.c.id).limit(limit).offset(offset)

        rows = await self._session.execute(select_stmt)

        return [dict(row) for row in rows.mappings().all()]
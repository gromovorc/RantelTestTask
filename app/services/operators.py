from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from app.db.tables import operators_table

class OperatorsService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_operator(self, name: str, email: str, status: str = "offline") -> dict:

        insert_stmt = pg_insert(operators_table).values(
            name=name,
            email=email,
            status=status
        ).returning(
            operators_table.c.id,
            operators_table.c.name,
            operators_table.c.email,
            operators_table.c.status
        )

        result = await self._session.execute(insert_stmt)

        await self._session.commit()

        return dict(result.mappings().one())

    async def get_operator(self, operator_id: int) -> dict | None:

        select_stmt = sa.select(
            operators_table.c.id,
            operators_table.c.name,
            operators_table.c.email,
            operators_table.c.status,
        ).where(operators_table.c.id == operator_id)

        rows = await self._session.execute(select_stmt)

        row = rows.mappings().one_or_none()

        return dict(row) if row else None

    async def get_operators_list(self, limit: int = 20, offset: int = 0) -> list[dict]:
        select_stmt = sa.select(
            operators_table.c.id,
            operators_table.c.name,
            operators_table.c.email,
        ).order_by(operators_table.c.id).limit(limit).offset(offset)

        rows = await self._session.execute(select_stmt)

        return [dict(row) for row in rows.mappings().all()]

    async def update_operator(self,
                              operator_id: int,
                              name: str | None = None,
                              email: str | None = None,
                              status: str | None = None) -> dict:

        update_stmt = (
            sa.update(operators_table)
            .where(operators_table.c.id == operator_id)
        )

        values = {
            column: new_value for column, new_value in (
                ("name", name), ("email", email), ("status", status)
            ) if new_value is not None
        }

        if not values:
            raise ValueError

        values["last_updated"] = sa.func.now()

        result = await self._session.execute(update_stmt.values(values).returning(
            operators_table.c.id,
            operators_table.c.name,
            operators_table.c.email,
            operators_table.c.status
        ))

        await self._session.commit()

        row = result.mappings().one_or_none()

        return dict(row) if row else None

    async def delete_operator(self, operator_id: int) -> bool:
        stmt = sa.delete(operators_table).where(operators_table.c.id == operator_id).returning(operators_table.c.id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        await self._session.commit()
        return deleted_id is not None

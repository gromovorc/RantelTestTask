from sqlalchemy import RowMapping
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from app.db.tables import messages_table

def _row_to_dict(row: dict | RowMapping) -> dict:
    result = dict(row)
    result["message_time"] = result.pop("instance_created").isoformat()
    return result

class MessagesService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_message(self,
                          author_type: str,
                          author_id: int,
                          text: str | None,
                          ticket_id: int) -> dict:

        insert_stmt = pg_insert(messages_table).values(
            author_type=author_type,
            author_id=author_id,
            text=text,
            ticket_id=ticket_id
        ).returning(
            messages_table.c.id,
            messages_table.c.text,
            messages_table.c.author_type,
            messages_table.c.author_id,
            messages_table.c.ticket_id,
            messages_table.c.instance_created
        )

        result = await self._session.execute(insert_stmt)
        await self._session.commit()
        return _row_to_dict(result.mappings().one())

    async def get_message(self, message_id: int) -> dict | None:

        select_stmt = sa.select(
            messages_table.c.id,
            messages_table.c.ticket_id,
            messages_table.c.author_type,
            messages_table.c.author_id,
            messages_table.c.text,
            messages_table.c.instance_created,
        ).where(messages_table.c.id == message_id)

        rows = await self._session.execute(select_stmt)

        row = rows.mappings().one_or_none()

        return _row_to_dict(row) if row else None

    async def get_messages_list(self,
                                ticket_id: int,
                                limit: int = 20,
                                offset: int = 0) -> list[dict]:
        select_stmt = (
            sa.select(
                messages_table.c.id,
                messages_table.c.ticket_id,
                messages_table.c.author_type,
                messages_table.c.author_id,
                messages_table.c.text,
                messages_table.c.instance_created,
            )
            .where(messages_table.c.ticket_id == ticket_id)
            .order_by(messages_table.c.id.asc())
            .limit(limit)
            .offset(offset)
        )

        rows = await self._session.execute(select_stmt)

        return [_row_to_dict(row) for row in rows.mappings().all()]

    async def update_message(
            self,
            message_id: int,
            text: str | None = None) -> dict:

        update_stmt = (
            sa.update(messages_table)
            .where(messages_table.c.id == message_id)
            .values(
                text=text,
                last_updated=sa.func.now()
            )
            .returning(messages_table.c.id,
                       messages_table.c.author_type,
                       messages_table.c.author_id,
                       messages_table.c.text,
                       messages_table.c.instance_created
                       )
        )


        result = await self._session.execute(update_stmt)

        await self._session.commit()

        row = result.mappings().one_or_none()

        return _row_to_dict(row) if row else None

    async def delete_message(self, message_id: int) -> bool:
        stmt = sa.delete(messages_table).where(messages_table.c.id == message_id).returning(messages_table.c.id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        await self._session.commit()
        return deleted_id is not None


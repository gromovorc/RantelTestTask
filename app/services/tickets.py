from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from app.db.tables import tickets_table, operators_table, messages_table


class TicketsService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_ticket(self, client_id: int, priority: str, subject: str, operator_id: int | None = None) -> dict:

        if operator_id is None:
            select_stmt = (
                sa.select(operators_table.c.id)
                .outerjoin(tickets_table,
                           sa.and_(
                               tickets_table.c.operator_id == operators_table.c.id,
                               tickets_table.c.status.in_(["in_progress", "waiting"])
                           ),
                           )
                .where(operators_table.c.status == "online")
                .group_by(operators_table.c.id)
                .order_by(sa.func.count(tickets_table.c.id).asc(), operators_table.c.id.asc())
                .limit(1)
            )

            result = await self._session.execute(select_stmt)

            operator_id = result.scalar_one_or_none()

        status = "in_progress" if operator_id is not None else "new"

        insert_stmt = (pg_insert(tickets_table)
        .values(
            client_id=client_id,
            priority=priority,
            subject=subject,
            operator_id=operator_id,
            status=status,
        ).returning(
            tickets_table.c.id,
            tickets_table.c.client_id,
            tickets_table.c.operator_id,
            tickets_table.c.priority,
            tickets_table.c.subject,
            tickets_table.c.status
        ))

        result = await self._session.execute(insert_stmt)

        await self._session.commit()

        return dict(result.mappings().one())

    async def get_ticket(self, ticket_id: int) -> dict | None:

        select_stmt = sa.select(
            tickets_table.c.id,
            tickets_table.c.priority,
            tickets_table.c.status,
            tickets_table.c.subject,
            tickets_table.c.operator_id,
            tickets_table.c.client_id,
        ).where(tickets_table.c.id == ticket_id)

        rows = await self._session.execute(select_stmt)

        row = rows.mappings().one_or_none()

        return dict(row) if row else None

    async def get_ticket_list(self, limit: int = 20, offset: int = 0) -> list[dict]:

        select_stmt = sa.select(
            tickets_table.c.id,
            tickets_table.c.priority,
            tickets_table.c.status,
            tickets_table.c.subject,
            tickets_table.c.operator_id,
            tickets_table.c.client_id,
        ).order_by(tickets_table.c.id).limit(limit).offset(offset)

        rows = await self._session.execute(select_stmt)

        return [dict(row) for row in rows.mappings().all()]

    async def get_ticket_status(self, ticket_id: int) -> str:

        select_stmt = sa.select(tickets_table.c.status).where(tickets_table.c.id == ticket_id)

        rows = await self._session.execute(select_stmt)

        row = rows.scalar_one_or_none()

        return row

    async def update_ticket(
            self,
            ticket_id: int,
            priority: str | None,
            status: str| None,
            subject: str | None,
            operator_id: int | None,
            client_id: int | None
    ) -> dict:
        if status is not None and status == "closed":
            if operator_id is None:
                select_stmt = sa.select(tickets_table.c.operator_id).where(tickets_table.c.id == ticket_id)

                rows = await self._session.execute(select_stmt)
                operator_id = rows.scalar_one_or_none()

            if operator_id is not None:
                priority_rank = sa.case(
                    (tickets_table.c.priority == "low", 1),
                    (tickets_table.c.priority == "normal", 2),
                    (tickets_table.c.priority == "high", 3),
                    else_=0,
                )

                select_next_stmt = (
                    sa.select(tickets_table.c.id)
                    .where(
                        tickets_table.c.operator_id.is_(None),
                        tickets_table.c.status == "new",
                    )
                    .order_by(priority_rank.desc(), tickets_table.c.instance_created.asc())
                    .limit(1)
                )

                result = await self._session.execute(select_next_stmt)
                next_ticket_id = result.scalar_one_or_none()

                if next_ticket_id is not None:

                    update_next_stmt = (
                        sa.update(tickets_table)
                        .where(tickets_table.c.id == next_ticket_id)
                        .values(
                            operator_id=operator_id,
                            status="in_progress",
                            status_last_updated=sa.func.now(),
                            last_updated=sa.func.now()
                        )
                    )

                    await self._session.execute(update_next_stmt)


        update_stmt = (sa.update(tickets_table)
                       .where(tickets_table.c.id == ticket_id)
        )

        values = {
            column: new_value for column, new_value in (
                ("priority", priority),
                ("status", status),
                ("subject", subject),
                ("operator_id", operator_id),
                ("client_id", client_id)
            ) if new_value is not None
        }
        if status is not None:
            values["status_last_updated"] = sa.func.now()
        values["last_updated"] = sa.func.now()

        result = await self._session.execute(update_stmt.values(values).returning(
            tickets_table.c.id,
            tickets_table.c.priority,
            tickets_table.c.status,
            tickets_table.c.subject,
            tickets_table.c.operator_id,
            tickets_table.c.client_id,
        ))

        await self._session.commit()

        row = result.mappings().one_or_none()

        return dict(row) if row else None

    async def delete_ticket(self, ticket_id: int) -> bool:

        await self._session.execute(
            sa.delete(messages_table).where(messages_table.c.ticket_id == ticket_id)
        )

        result = await self._session.execute(
            sa.delete(tickets_table).where(tickets_table.c.id == ticket_id).returning(tickets_table.c.id)
        )
        deleted_id = result.scalar_one_or_none()
        await self._session.commit()
        return deleted_id is not None


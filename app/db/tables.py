from sqlalchemy import Table, Column, ForeignKey, Text, DateTime, MetaData, BigInteger, func, UniqueConstraint, Index, \
    Identity, CheckConstraint

_metadata = MetaData()

clients_table = Table(
    "clients",
    _metadata,
    Column('id', BigInteger, Identity(), primary_key=True),
    Column('name', Text, nullable=False),
    Column('email', Text, nullable=False),

    Column('instance_created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('last_updated', DateTime(timezone=True), nullable=False, server_default=func.now()),

    UniqueConstraint("name", "email", name="uix_clients_name_email")
)

operators_table = Table(
    "operators",
    _metadata,
    Column('id', BigInteger, Identity(), primary_key=True),
    Column('name', Text, nullable=False),
    Column('email', Text, nullable=False),
    Column('status', Text, nullable=False),

    Column('instance_created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('last_updated', DateTime(timezone=True), nullable=False, server_default=func.now()),

    UniqueConstraint("name", "email", name="uix_operators_name_email"),
    CheckConstraint("status IN ('online', 'offline', 'busy')", name="ck_operators_check_status")
)

tickets_table = Table(
    "tickets",
    _metadata,
    Column('id', BigInteger, Identity(), primary_key=True),
    Column('client_id', BigInteger, ForeignKey("clients.id"), nullable=False),
    Column('operator_id', BigInteger, ForeignKey("operators.id"), nullable=True),
    Column('status', Text, nullable=False),
    Column('status_last_updated', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('priority', Text, nullable=False),
    Column('subject', Text, nullable=False),

    Column('instance_created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('last_updated', DateTime(timezone=True), nullable=False, server_default=func.now()),

    CheckConstraint("status IN ('new', 'in_progress', 'waiting', 'resolved', 'closed')", name="ck_tickets_check_status"),
    CheckConstraint("priority IN ('low', 'normal', 'high')", name="ck_tickets_check_priority"),

    Index("idx_client", "client_id"),
    Index("idx_operator", "operator_id"),
    Index("idx_operator_status", "operator_id", "status"),
    Index("idx_status", "status"),
    Index("idx_status_last_updated", "status_last_updated"),
)

messages_table = Table(
    "messages",
    _metadata,
    Column('id', BigInteger, Identity(), primary_key=True),
    Column('ticket_id', BigInteger, ForeignKey("tickets.id"), nullable=False),
    Column('author_type', Text, nullable=True),
    Column('author_id', Text, nullable=True),
    Column('text', Text, nullable=False),

    Column('instance_created', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('last_updated', DateTime(timezone=True), nullable=False, server_default=func.now()),

    CheckConstraint("author_type IN ('client', 'operator')", name="ck_messages_check_author_type")
)
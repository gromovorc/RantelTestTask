from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

engine = create_async_engine(
        settings.database_url,
        echo=True,
    )

async_session_maker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False, # часто удобнее для async-сценариев
    )

async def get_session():
    async with async_session_maker() as session:
        yield session

from contextlib import asynccontextmanager

from typing import Annotated
from datetime import datetime

from sqlalchemy import func, text
from sqlalchemy.orm import Mapped, sessionmaker, declarative_base, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs, create_async_engine


DeclarativeBase = declarative_base()

int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)
]

str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int_pk]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id!r})"


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url)
        self._session_factory = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_models(self):
        async with self._engine.begin() as session:
            await session.run_sync(Base.metadata.drop_all)
            await session.run_sync(Base.metadata.create_all)

    async def add_trgm(self):
        async with self._session_factory() as session:
            await session.execute(text(
                'CREATE EXTENSION IF NOT EXISTS pg_trgm')
            )
            await session.commit()

    async def drop_models(self):
        async with self._engine.begin() as session:
            await session.run_sync(Base.metadata.drop_all)

    @asynccontextmanager
    async def session(self):
        async with self._session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

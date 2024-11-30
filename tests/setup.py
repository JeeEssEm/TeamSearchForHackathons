import pytest

from core.database import Database, Base

pytest_plugins = ["pytest_asyncio"]
db = Database("sqlite+aiosqlite:///./test_db.sqlite")


@pytest.fixture(scope="session")
async def test_db():
    await db.init_models()


@pytest.fixture(scope="session")
async def drop_db():
    await db.drop_models()


async def create_entity(model):
    async with db.session() as s:
        s.add(model)
        await s.commit()

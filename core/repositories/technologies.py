from .base import Repository
import core.models as models
from core.dtos import Technology


class TechnologiesRepository(Repository):
    async def create(self, title: str) -> Technology:
        tech = models.Technology(title=title)
        self.session.add(tech)
        await self.session.commit()
        return tech.convert_to_dto()

    async def check_if_same_exists(self, title: str) -> bool:
        return False

    async def get_same_technologies(self, title: str) -> list[Technology]:
        return [...]

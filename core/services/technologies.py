from .base import Service
from core.repositories import TechnologiesRepository
from core.dtos import TechnologyResponse, ResponseStatus
from core.config import settings


class TechnologiesService(Service):
    repository: TechnologiesRepository

    async def create_technology(self, title: str) -> TechnologyResponse:
        # тут может быть какая-нибудь логика
        # например, поиск похожих по названию технологий и обработка случая,
        # когда похожая технология найдена
        if await self.repository.check_if_same_exists(title):
            return TechnologyResponse(
                status=ResponseStatus.already_exists,
                technology=await self.repository.get_same_technologies(title),
                message="Технологии с похожим названием уже существуют",
            )
        # какая-нибудь проверка на уровень доверия к пользователю
        status = ResponseStatus.object_created
        if settings.TRUST_FACTOR:
            status = ResponseStatus.in_review
        return TechnologyResponse(
            status=status,
            technology=await self.repository.create(title),
            message=None,
        )

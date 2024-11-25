from dependency_injector import containers, providers

from core.database import Database
from core.services import TechnologiesService
from core.repositories import TechnologiesRepository
from core.config import get_database_url


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Singleton(
        Database,
        db_url=get_database_url(),
    )

    technology_service = providers.Factory(
        TechnologiesService.constructor,
        factory=db.provided.session
    )
    technology_repository = providers.Factory(
        TechnologiesRepository.constructor,
        factory=db.provided.session
    )

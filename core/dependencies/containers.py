from dependency_injector import containers, providers

from core.database import Database
from core.services import TechnologiesService
from core.config import get_database_url


class ServiceContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Singleton(
        Database,
        db_url=get_database_url(),
    )

    technology_service = providers.Factory(
        TechnologiesService.constructor,
        factory=db.provided.session
    )

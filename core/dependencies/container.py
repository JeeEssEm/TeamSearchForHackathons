from dependency_injector import containers, providers

from core.database import Database
from core.config import get_database_url


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Singleton(
        Database,
        db_url=get_database_url(),
    )

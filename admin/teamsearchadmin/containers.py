from dependency_injector import containers, providers


class Service:
    def test(self):
        return 'tested'


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    service = providers.Factory(Service)

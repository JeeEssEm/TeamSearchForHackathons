from . import settings
from core.dependencies.containers import ServiceContainer

container = ServiceContainer()
container.config.from_dict(settings.__dict__)

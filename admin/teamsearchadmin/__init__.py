from . import settings
from core.dependencies.container import Container

container = Container()
container.config.from_dict(settings.__dict__)

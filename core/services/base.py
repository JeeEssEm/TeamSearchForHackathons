from core.dependencies.base import BaseWithSessionObject


class Service(BaseWithSessionObject):
    def __init__(self, session):
        annotations = self.__class__.__annotations__
        self.repository = annotations['repository'](session)

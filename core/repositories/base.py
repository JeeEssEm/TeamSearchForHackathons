from core.database import AsyncSession
from core.dependencies.base import BaseWithSessionObject


class Repository(BaseWithSessionObject):
    def __init__(self, session: AsyncSession):
        self.session = session

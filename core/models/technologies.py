from sqlalchemy.orm import Mapped

from core import dtos
from core.database import Base


class Technology(Base):
    __tablename__ = "technologies"
    title: Mapped[str]

    def convert_to_dto(self):
        return dtos.Technology(
            id=self.id,
            title=self.title,
        )

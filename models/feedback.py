
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import Integer, ForeignKey, String

from database import AbstractBase

if TYPE_CHECKING:
    from .user import User

class Feedback(AbstractBase):
    __tablename__ ="feedbacks"
    
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    sender: Mapped['User'] = relationship("User", foreign_keys=[sender_id], back_populates="sent_feedbacks")

    receiver_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    receiver: Mapped['User'] = relationship("User", foreign_keys=[receiver_id], back_populates="received_feedbacks")
    
    feedback: Mapped[str] = mapped_column(String(300), nullable=False)
    
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class UsersForms:
    __tablename__ = 'users_forms' 
    id:Mapped[int] = mapped_column(Integer, primary_key= True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), ondelete="CASCADE")
    form_id:Mapped[int] = mapped_column(Integer, ForeignKey('forms.id'), ondelete="CASCADE")

        
    # Добавление индексов для быстрого поиска (не совсем понятно)
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
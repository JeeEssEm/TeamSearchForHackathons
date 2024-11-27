from sqlalchemy import Table, Column, Integer, ForeignKey
from database import Base

users_roles = Table(
    'users_roles',
    Base.metadata,
    Column(
        'user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True
    ),
    Column(
        'role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True
    ),
)

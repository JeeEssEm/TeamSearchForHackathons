from sqlalchemy import create_engine, Integer
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:i2903T1505@localhost:5432/ITAM_pj'

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class AbstractBase(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    @property
    def __tablename__(cls):
        return cls.__name__.lower()

from fastapi import FastAPI, Depends

from sqlalchemy.exc import OperationalError
from database import SessionLocal
from sqlalchemy import text
from sqlalchemy.orm import Session
from models import *
from database import Base, engine

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ДЛЯ ПРОВЕРКИ ПОДКЛЮЧЕНИЯ К БД
@app.get("/check_db_connection")
def check_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "Database connection is successful"}
    except OperationalError:
        return {"status": "Database connection failed"}


Base.metadata.create_all(engine)

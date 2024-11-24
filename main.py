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


# from sqlalchemy.orm import Session
# from models import User, Feedback

# # Создаём сессию
# session = Session()

# # Добавляем двух пользователей
# user1 = User(name="Alice")
# user2 = User(name="Bob")
# session.add_all([user1, user2])
# session.commit()

# # Добавляем отзыв от Alice к Bob
# feedback = Feedback(sender_id=user1.id, receiver_id=user2.id, feedback="Great work!")
# session.add(feedback)
# session.commit()

# # Проверяем данные
# sent = session.query(User).filter_by(name="Alice").first()
# print(f"Sent Feedbacks: {sent.sent_feedbacks}")

# received = session.query(User).filter_by(name="Bob").first()
# print(f"Received Feedbacks: {received.received_feedbacks}")
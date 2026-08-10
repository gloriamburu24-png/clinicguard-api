from database.session import engine
from sqlmodel import Session, select
from models.user import User

with Session(engine) as session:
    users = session.exec(select(User)).all()
    print("Number of users:", len(users))
    for u in users:
        print(f"{u.username} - {u.email} - {u.role}")
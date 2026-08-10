from database.session import engine
from sqlmodel import Session
from models.user import User
from auth import hash_password

user = User(
    username="admin",
    email="admin@clinic.com",
    hashed_password=hash_password("admin1234"),
    full_name="System Administrator",
    role="admin"
)

with Session(engine) as session:
    session.add(user)
    session.commit()
    print("✅ User created successfully!")
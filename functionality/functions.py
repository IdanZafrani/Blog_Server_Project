from sqlalchemy.orm import sessionmaker
from modelsPack.models import User, Like, Blog
from sqlalchemy import create_engine
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status

# Configure the database connection
DATABASE_URL = 'sqlite:///./modelsPack/blogs.db'
engine = create_engine(DATABASE_URL)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

security = HTTPBasic()


def add_user_credentials_to_db(name: str, password: str):
    find_user_in_db = session.query(User).filter(User.username == name).first()
    if not find_user_in_db:
        new_user = User(username=name, password=password)
        session.add(new_user)
        session.commit()


def authentication_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = session.query(User).filter(credentials.username == User.username,
                                      credentials.password == User.password).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"{credentials.username} - username or password are not correct or exist")
    return user
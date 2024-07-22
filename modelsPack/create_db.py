# database/create_db.py
from sqlalchemy import create_engine
from modelsPack.models import Base

# DATABASE_URL = ('sqlite://///Blog_Server_BackEnd/modelsPack'
#                 '/blogs.db')
# Relative path inside the container
relative_path = '/app/modelsPack/blogs.db'

# Construct the database URL using the relative path
DATABASE_URL = f'sqlite:///{relative_path}'


def create_database(database_url: str):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine

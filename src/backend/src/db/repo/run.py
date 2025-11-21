
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import text
from src.backend.src.db.repo.db_setup import Base
from src.backend.src.db.models.listing import Listing
from src.backend.src.db.models.movie import Movie
from src.backend.src.db.models.venue import Venue
DATABASE_URL = "postgresql://user:password@localhost:5432/cinema"

engine = create_engine(DATABASE_URL)

def get_connection():
    session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return session_maker()


if __name__ == "__main__":
    create_role_sql = """
    CREATE ROLE cinema WITH LOGIN PASSWORD 'password';
    """

    with engine.connect() as connection:
        connection.execute(text(create_role_sql))
        Base.metadata.create_all(bind=engine)


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import text
from src.backend.db.repo.db_setup import Base
from src.backend.db.models.listing import Listing
from src.backend.db.models.movie import Movie
from src.backend.db.models.venue import Venue
DATABASE_URL = "postgresql://user:password@localhost:5432/cinema"

engine = create_engine(DATABASE_URL)

session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)


if __name__ == "__main__":
    create_role_sql = """
    CREATE ROLE cinema WITH LOGIN PASSWORD 'password';
    """

    with engine.connect() as connection:
        connection.execute(text(create_role_sql))
        Base.metadata.create_all(bind=engine)

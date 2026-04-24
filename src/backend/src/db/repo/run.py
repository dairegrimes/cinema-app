from db.models import listing, movie, venue  # noqa: F401 – registers models with Base
from db.repo.db_setup import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")

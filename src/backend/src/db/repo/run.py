from db.models import (  # noqa: F401 – registers models with Base
    listing,
    movie,
    sent_alert,
    subscription,
    venue,
)
from db.repo.db_setup import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")

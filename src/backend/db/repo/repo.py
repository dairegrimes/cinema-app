from src.backend.db.repo.run import session_maker
from src.backend.db.models.listing import Listing


class Repo:
    def __init__(self):
        pass

    def get_listings(self):
        session = session_maker()
        return session.query(Listing).all()

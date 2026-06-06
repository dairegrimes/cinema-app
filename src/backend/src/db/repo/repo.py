from sqlalchemy.orm import Session, joinedload

from db.models.listing import Listing
from db.models.movie import Movie
from db.models.venue import Venue


class Repo:
    def get_listings(self, db: Session) -> list[Listing]:
        return (
            db.query(Listing)
            .options(joinedload(Listing.movie), joinedload(Listing.venue))
            .all()
        )

    def get_movies(self, db: Session) -> list[Movie]:
        return db.query(Movie).all()

    def get_venues(self, db: Session) -> list[Venue]:
        return db.query(Venue).all()

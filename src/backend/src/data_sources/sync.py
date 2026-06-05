import hashlib
import logging

from sqlalchemy.orm import Session

from data_sources.scrapers.dublin_rathmines import ListingDC
from db.models.listing import Listing
from db.models.movie import Movie
from db.models.venue import Venue

logger = logging.getLogger(__name__)


def _get_or_create_venue(db: Session, name: str) -> Venue:
    venue = db.query(Venue).filter(Venue.name == name).first()
    if not venue:
        venue = Venue(name=name)
        db.add(venue)
        db.flush()
    return venue


def _get_or_create_movie(db: Session, name: str) -> Movie:
    movie = db.query(Movie).filter(Movie.name == name).first()
    if not movie:
        movie = Movie(name=name)
        db.add(movie)
        db.flush()
    return movie


def _make_listing_id(venue_name: str, movie_name: str, timestamp: int) -> str:
    raw = f"{venue_name}|{movie_name}|{timestamp}"
    return hashlib.sha1(raw.encode()).hexdigest()


def sync_listings(db: Session, listings: list[ListingDC]) -> tuple[int, int]:
    """Upsert listings into the database.

    Returns (inserted, skipped) counts.
    """
    inserted = 0
    skipped = 0
    for ldc in listings:
        venue = _get_or_create_venue(db, ldc.venue)
        movie = _get_or_create_movie(db, ldc.movie)
        timestamp = int(ldc.time.timestamp())
        listing_id = _make_listing_id(ldc.venue, ldc.movie, timestamp)

        exists = db.query(Listing).filter(Listing._listing_id == listing_id).first()
        if exists:
            skipped += 1
            continue

        listing = Listing(movie=movie, time=ldc.time, venue=venue, maxx=ldc.maxx)
        listing.listing_id = listing_id
        db.add(listing)
        inserted += 1

    return inserted, skipped

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas.listing import ListingOut
from db.repo.db_setup import get_db
from db.repo.repo import Repo

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/", response_model=list[ListingOut])
def get_listings(db: Session = Depends(get_db)):
    listings = Repo().get_listings(db)
    return [
        ListingOut(
            id=listing.id,
            movie=listing.movie.name,
            venue=listing.venue.name,
            time=listing.time,
            maxx=listing.maxx,
        )
        for listing in listings
    ]

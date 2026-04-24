from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.repo.db_setup import get_db
from db.repo.repo import Repo

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/")
def get_listings(db: Session = Depends(get_db)):
    return Repo().get_listings(db)

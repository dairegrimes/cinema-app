from fastapi import APIRouter

from src.backend.db.repo.repo import Repo

router = APIRouter()


@router.get("/listing")
async def root():
    data = Repo().get_listings()
    return data

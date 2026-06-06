from pydantic import BaseModel


class ListingOut(BaseModel):
    id: int
    movie: str
    venue: str
    time: int
    maxx: bool

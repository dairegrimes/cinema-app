from typing import Optional

from pydantic import BaseModel, EmailStr


class SubscriptionCreate(BaseModel):
    email: EmailStr
    movie_name: str
    venue_name: Optional[str] = None


class SubscriptionCreated(BaseModel):
    status: str
    message: str

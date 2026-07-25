import secrets
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from db.repo.db_setup import Base


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


class Subscription(Base):
    __tablename__ = 'subscription'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, index=True)
    movie_name = Column(String, nullable=False)
    venue_name = Column(String, nullable=True)
    token = Column(String, nullable=False, unique=True, default=_generate_token)
    confirmed = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    sent_alerts = relationship(
        "SentAlert", back_populates="subscription", cascade="all, delete-orphan"
    )

    def __init__(self, email, movie_name, venue_name=None):
        self.email = email
        self.movie_name = movie_name
        self.venue_name = venue_name
        self.token = _generate_token()
        self.confirmed = False
        self.active = True

    def __repr__(self):
        return f"Subscription({self.email}, {self.movie_name}, venue={self.venue_name})"

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.backend.db.repo.db_setup import Base


class Venue(Base):
    __tablename__ = 'venue'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    listing = relationship("Listing", back_populates="venue")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"({self.name})"

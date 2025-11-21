from sqlalchemy import Boolean, BigInteger, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from src.backend.src.db.repo.db_setup import Base


class Listing(Base):

    __tablename__ = 'listing'
    id = Column(Integer, primary_key=True, autoincrement=True)
    _listing_id = Column('listing_id', String, unique=True, nullable=False)
    time = Column(BigInteger, nullable=False)
    venue_id = Column(Integer, ForeignKey('venue.id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movie.id'), nullable=False)
    maxx = Column(Boolean, default=False, nullable=False)

    venue = relationship("Venue", back_populates="listing")
    movie = relationship("Movie", back_populates="listing")

    def __init__(self, movie, time, venue, maxx=False):
        self.movie = movie
        self.time = int(time.timestamp())
        self.venue = venue
        self.maxx = maxx
        self._listing_id = None

    def __repr__(self):
        return f"({self.movie}, {self.time}, {self.maxx}, {self.venue})"

    @hybrid_property
    def venue_property(self):
        return self.venue_id

    @venue_property.setter
    def venue_property(self, value):
        self.venue_id = value

    @hybrid_property
    def movie_property(self):
        return self.movie_id

    @movie_property.setter
    def movie_property(self, value):
        self.movie_id = value

    @property
    def listing_id(self):
        return self._listing_id

    @listing_id.setter
    def listing_id(self, value):
        self._listing_id = value

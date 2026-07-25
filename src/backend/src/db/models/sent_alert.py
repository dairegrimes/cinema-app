from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from db.repo.db_setup import Base


class SentAlert(Base):
    """Records that a subscriber has been alerted about a movie.

    The unique (subscription_id, movie_name) constraint guarantees a subscriber
    is emailed at most once per movie, even as more showtimes are scraped.
    """

    __tablename__ = 'sent_alert'
    __table_args__ = (
        UniqueConstraint('subscription_id', 'movie_name', name='uq_sent_alert_sub_movie'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(
        Integer, ForeignKey('subscription.id', ondelete='CASCADE'), nullable=False
    )
    movie_name = Column(String, nullable=False)
    sent_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    subscription = relationship("Subscription", back_populates="sent_alerts")

    def __init__(self, subscription_id, movie_name):
        self.subscription_id = subscription_id
        self.movie_name = movie_name

    def __repr__(self):
        return f"SentAlert(sub={self.subscription_id}, {self.movie_name})"

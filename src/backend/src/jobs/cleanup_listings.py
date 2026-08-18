"""Daily cleanup job: delete listings whose showtime has passed.

Run with:
    python -m jobs.cleanup_listings
"""
import logging
import os
import sys
import time

from db.models.listing import Listing
from db.repo.db_setup import SessionLocal
from db.repo.run import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s – %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Grace period after a showing's start time before it's considered
# "completed" and eligible for cleanup, to avoid deleting a listing
# while it may still be playing.
GRACE_PERIOD_HOURS = float(os.environ.get("CLEANUP_GRACE_HOURS", "3"))


def run() -> None:
    init_db()
    db = SessionLocal()
    try:
        cutoff = int(time.time()) - int(GRACE_PERIOD_HOURS * 3600)
        deleted = (
            db.query(Listing)
            .filter(Listing.time < cutoff)
            .delete(synchronize_session=False)
        )
        db.commit()
        logger.info("Deleted %d completed listing(s)", deleted)
    except Exception:
        db.rollback()
        logger.exception("Unexpected error, rolling back")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()

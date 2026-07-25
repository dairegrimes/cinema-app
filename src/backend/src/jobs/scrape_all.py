"""Entrypoint for the daily scrape job.

Run with:
    python -m jobs.scrape_all
"""
import logging
import sys

from data_sources.notify import notify_subscribers
from data_sources.scrapers import dublin_rathmines
from data_sources.sync import sync_listings
from db.models import (  # noqa: F401 – registers models with Base
    listing,
    movie,
    sent_alert,
    subscription,
    venue,
)
from db.repo.db_setup import SessionLocal
from db.repo.run import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s – %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

SCRAPERS = [
    dublin_rathmines,
]


def run() -> None:
    init_db()
    db = SessionLocal()
    total_inserted = 0
    total_skipped = 0
    all_new_listings = []
    errors = []

    try:
        for scraper in SCRAPERS:
            name = scraper.VENUE_NAME
            logger.info("Scraping %s …", name)
            try:
                listings = scraper.scrape()
                logger.info("  fetched %d listings", len(listings))
                inserted, skipped, new_listings = sync_listings(db, listings)
                logger.info("  inserted=%d skipped=%d", inserted, skipped)
                total_inserted += inserted
                total_skipped += skipped
                all_new_listings.extend(new_listings)
            except Exception:
                logger.exception("  failed to scrape %s", name)
                errors.append(name)

        # Persist listings first so alert emails only reflect committed data.
        db.commit()

        if all_new_listings:
            notify_subscribers(db, all_new_listings)
            db.commit()

        logger.info(
            "Done – total inserted=%d skipped=%d errors=%d",
            total_inserted,
            total_skipped,
            len(errors),
        )
    except Exception:
        db.rollback()
        logger.exception("Unexpected error, rolling back")
        raise
    finally:
        db.close()

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    run()

"""Match newly scraped listings against subscriptions and send alert emails."""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func
from sqlalchemy.orm import Session

from common.config import unsubscribe_url
from common.email import send_email
from db.models.listing import Listing
from db.models.sent_alert import SentAlert
from db.models.subscription import Subscription

logger = logging.getLogger(__name__)


def _format_time(epoch: int) -> str:
    dt = datetime.fromtimestamp(epoch, tz=ZoneInfo("Europe/Dublin"))
    return dt.strftime("%a %d %b, %H:%M")


def _matching_subscriptions(db: Session, movie_name: str, venue_name: str) -> list[Subscription]:
    return (
        db.query(Subscription)
        .filter(
            Subscription.confirmed.is_(True),
            Subscription.active.is_(True),
            func.lower(Subscription.movie_name) == movie_name.lower(),
        )
        .filter(
            (Subscription.venue_name.is_(None))
            | (func.lower(Subscription.venue_name) == venue_name.lower())
        )
        .all()
    )


def _build_email(sub: Subscription, movie_name: str, venue_name: str, showtime: str):
    subject = f"🎬 {movie_name} is now showing at {venue_name}"
    unsub = unsubscribe_url(sub.token)
    text_body = (
        f"Good news! {movie_name} is now scheduled at {venue_name}.\n\n"
        f"First showtime: {showtime}\n\n"
        f"You're receiving this because you subscribed to alerts for this movie.\n"
        f"Unsubscribe: {unsub}\n"
    )
    html_body = (
        f"<h2>🎬 {movie_name} is now showing!</h2>"
        f"<p><strong>{movie_name}</strong> is now scheduled at <strong>{venue_name}</strong>.</p>"
        f"<p>First showtime: <strong>{showtime}</strong></p>"
        f"<hr/>"
        f"<p style='color:#888;font-size:12px'>You're receiving this because you "
        f"subscribed to alerts for this movie. "
        f"<a href='{unsub}'>Unsubscribe</a></p>"
    )
    return subject, html_body, text_body


def notify_subscribers(db: Session, new_listings: list[Listing]) -> int:
    """For each new listing, email matching subscribers (once per movie).

    Returns the number of alert emails sent. Caller is responsible for
    committing the session afterwards.
    """
    sent_count = 0
    # Track (subscription_id, movie_name) handled in this run to avoid
    # duplicate work when a movie has many new showtimes at once.
    handled: set[tuple[int, str]] = set()

    for listing in new_listings:
        movie_name = listing.movie.name
        venue_name = listing.venue.name
        showtime = _format_time(int(listing.time))

        for sub in _matching_subscriptions(db, movie_name, venue_name):
            key = (sub.id, movie_name.lower())
            if key in handled:
                continue
            handled.add(key)

            already = (
                db.query(SentAlert)
                .filter(
                    SentAlert.subscription_id == sub.id,
                    func.lower(SentAlert.movie_name) == movie_name.lower(),
                )
                .first()
            )
            if already:
                continue

            subject, html_body, text_body = _build_email(
                sub, movie_name, venue_name, showtime
            )
            try:
                send_email(sub.email, subject, html_body, text_body)
            except Exception:
                logger.exception("Failed to send alert to %s for %s", sub.email, movie_name)
                continue

            db.add(SentAlert(subscription_id=sub.id, movie_name=movie_name))
            db.flush()
            sent_count += 1

    logger.info("notify_subscribers sent %d alert email(s)", sent_count)
    return sent_count

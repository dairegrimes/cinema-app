import logging

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.schemas.subscription import SubscriptionCreate, SubscriptionCreated
from common.config import confirm_url
from common.email import send_email
from db.models.subscription import Subscription
from db.repo.db_setup import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


def _send_confirmation_email(sub: Subscription) -> None:
    link = confirm_url(sub.token)
    venue_part = f" at {sub.venue_name}" if sub.venue_name else ""
    subject = "Confirm your cinema alert"
    text_body = (
        f"Please confirm you want alerts for '{sub.movie_name}'{venue_part}.\n\n"
        f"Confirm: {link}\n\n"
        f"If you didn't request this, you can ignore this email."
    )
    html_body = (
        f"<h2>Confirm your cinema alert</h2>"
        f"<p>Please confirm you want alerts for "
        f"<strong>{sub.movie_name}</strong>{venue_part}.</p>"
        f"<p><a href='{link}' "
        f"style='display:inline-block;padding:10px 18px;background:#2563eb;"
        f"color:#fff;text-decoration:none;border-radius:6px'>Confirm subscription</a></p>"
        f"<p style='color:#888;font-size:12px'>If you didn't request this, ignore this email.</p>"
    )
    send_email(sub.email, subject, html_body, text_body)


def _page(title: str, message: str) -> HTMLResponse:
    html = (
        f"<!doctype html><html><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>{title}</title></head>"
        f"<body style='font-family:system-ui,sans-serif;background:#0a0a0a;color:#fff;"
        f"display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0'>"
        f"<div style='text-align:center;padding:2rem'>"
        f"<h1 style='margin-bottom:0.5rem'>{title}</h1>"
        f"<p style='color:#aaa'>{message}</p></div></body></html>"
    )
    return HTMLResponse(content=html)


@router.post("/", response_model=SubscriptionCreated, status_code=201)
def create_subscription(payload: SubscriptionCreate, db: Session = Depends(get_db)):
    venue_name = payload.venue_name or None

    query = db.query(Subscription).filter(
        func.lower(Subscription.email) == payload.email.lower(),
        func.lower(Subscription.movie_name) == payload.movie_name.lower(),
    )
    if venue_name is None:
        query = query.filter(Subscription.venue_name.is_(None))
    else:
        query = query.filter(func.lower(Subscription.venue_name) == venue_name.lower())
    existing = query.first()

    if existing:
        if existing.confirmed and existing.active:
            return SubscriptionCreated(
                status="exists",
                message="You're already subscribed to this alert.",
            )
        # Re-activate / re-send confirmation for an unconfirmed or cancelled sub.
        existing.active = True
        existing.confirmed = False
        db.commit()
        _send_confirmation_email(existing)
        return SubscriptionCreated(
            status="pending",
            message="Please check your email to confirm your subscription.",
        )

    sub = Subscription(
        email=str(payload.email),
        movie_name=payload.movie_name,
        venue_name=venue_name,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    try:
        _send_confirmation_email(sub)
    except Exception:
        logger.exception("Failed to send confirmation email to %s", sub.email)

    return SubscriptionCreated(
        status="pending",
        message="Please check your email to confirm your subscription.",
    )


@router.get("/confirm", response_class=HTMLResponse)
def confirm_subscription(token: str = Query(...), db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.token == token).first()
    if not sub:
        return _page("Invalid link", "This confirmation link is invalid or has expired.")

    if not sub.confirmed:
        sub.confirmed = True
        sub.active = True
        db.commit()

    return _page(
        "Subscription confirmed",
        f"You'll be alerted when '{sub.movie_name}' is scheduled.",
    )


@router.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe(token: str = Query(...), db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.token == token).first()
    if not sub:
        return _page("Invalid link", "This unsubscribe link is invalid.")

    if sub.active:
        sub.active = False
        db.commit()

    return _page("Unsubscribed", "You will no longer receive alerts for this movie.")

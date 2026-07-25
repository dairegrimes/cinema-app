import os

# Public base URL of the backend API, used to build links in emails
# (confirmation / unsubscribe). Override in production via env.
PUBLIC_API_URL = os.environ.get("PUBLIC_API_URL", "http://localhost:8000")


def confirm_url(token: str) -> str:
    return f"{PUBLIC_API_URL}/subscriptions/confirm?token={token}"


def unsubscribe_url(token: str) -> str:
    return f"{PUBLIC_API_URL}/subscriptions/unsubscribe?token={token}"

import re
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import requests
from bs4 import BeautifulSoup

from common.time_common import get_datetime

VENUE_NAME = "Omniplex Dublin Rathmines"
SITE_CODE = "OMP_RATH"
SHOWTIMES_URL = "https://www.omniplex.ie/cinema/showtimes"
SCRAPE_DAYS_AHEAD = 7

_SESSION = requests.Session()
_SESSION.cookies.set("sitecode", SITE_CODE, domain="www.omniplex.ie")

# e.g. "Scary Movie at 13:40 in MAXX 1"
_SHOWTIME_ARIA = re.compile(r"^(.+?) at (\d{1,2}:\d{2}) in ", re.IGNORECASE)


@dataclass
class ListingDC:
    movie: str
    time: datetime
    venue: str
    maxx: bool


def _parse_showtime(target_date: date, time_str: str) -> datetime:
    hour, minute = time_str.split(":")
    return get_datetime(target_date.year, target_date.month, target_date.day, int(hour), int(minute))


def _scrape_date(target_date: date) -> list[ListingDC]:
    response = _SESSION.get(
        SHOWTIMES_URL,
        params={"action": "processFilters", "filterDate": target_date.strftime("%Y-%m-%d")},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    listings: list[ListingDC] = []
    for link in soup.find_all("a", attrs={"aria-label": True}):
        match = _SHOWTIME_ARIA.match(link["aria-label"])
        if not match:
            continue
        listings.append(ListingDC(
            movie=match.group(1).strip(),
            time=_parse_showtime(target_date, match.group(2)),
            venue=VENUE_NAME,
            maxx="maxx" in link["aria-label"].lower(),
        ))
    return listings


def scrape() -> list[ListingDC]:
    listings: list[ListingDC] = []
    for offset in range(SCRAPE_DAYS_AHEAD):
        target_date = date.today() + timedelta(days=offset)
        listings.extend(_scrape_date(target_date))
        if offset < SCRAPE_DAYS_AHEAD - 1:
            time.sleep(0.5)
    return listings

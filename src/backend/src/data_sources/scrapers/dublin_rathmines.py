import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import requests
from bs4 import BeautifulSoup

from common.time_common import get_datetime

VENUE_NAME = "Omniplex Dublin Rathmines"
URL = "https://www.omniplex.ie/cinema/dublin-rathmines"
SCRAPE_DAYS_AHEAD = 7


@dataclass
class ListingDC:
    movie: str
    time: datetime
    venue: str
    maxx: bool


def _parse_time(data_date: str, time_str: str) -> datetime:
    day, month, year = data_date.split('-')
    hour, minute = time_str.split(':')
    return get_datetime(int(year), int(month), int(day), int(hour), int(minute))


def _scrape_date(target_date: date) -> list[ListingDC]:
    date_str = target_date.strftime("%d-%m-%Y")
    response = requests.get(URL, params={"date": date_str}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    listings: list[ListingDC] = []
    for movie in soup.find_all('div', class_=' '):
        if not movie.find(class_="OMP_buttonSelection"):
            continue
        movie_title = movie.find("h3", class_="OMP_inlineBlock").get_text(strip=True)
        for div in movie.find_all("div", class_="OMP_listingDate"):
            data_date = div.get("data-date")
            for a in div.find_all("a", class_="OMP_buttonSelection"):
                time_tag = a.find(class_='time')
                time_str = time_tag.contents[0].strip()
                if 'SoldOut' in time_str:
                    continue
                listings.append(ListingDC(
                    movie=movie_title,
                    time=_parse_time(data_date, time_str),
                    venue=VENUE_NAME,
                    maxx="maxx" in a.get("href", ""),
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


if __name__ == "__main__":
    listings = scrape()
    print(listings)

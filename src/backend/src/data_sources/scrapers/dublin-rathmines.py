from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from common.time_common import get_datetime
from db.models.listing import Listing
from db.models.movie import Movie
from db.models.venue import Venue

# from db.repo.run import session_maker


@dataclass
class ListingDC:
    movie: str
    time: datetime
    venue: str
    maxx: bool


def get_time(data_date: str, time: str) -> datetime:
    day, month, year = data_date.split('-')
    hour, minute = time.split(':')
    return get_datetime(int(year), int(month), int(day), int(hour), int(minute))


page_to_scrape = requests.get('https://www.omniplex.ie/cinema/dublin-rathmines')
soup = BeautifulSoup(page_to_scrape.text, "html.parser")
movies = soup.find('div', class_='OMP_mainContainer')
date_times = []
listings = []
movies_list = set()
movie_to_listing_mapping = defaultdict(list)

for movie in soup.find_all('div', class_='OMP_listingContainer'):
    button = movie.find(class_="OMP_buttonSelection")
    if button:
        movie_title = movie.find("h3", class_="OMP_inlineBlock").get_text()
        print(movie_title)
        time_divs = movie.find_all("div", class_="OMP_listingDate")
        for div in time_divs:
            data_date = div.get("data-date")
            for a in div.find_all("a", class_="OMP_buttonSelection"):
                time = a.find(class_='time')
                time = time.contents[0].strip()
                if 'SoldOut' in time:
                    continue
                time_object = get_time(data_date, time)
                maxx = True if "maxx" in a.get("href", "") else False
                movies_list.add(movie_title)
                listings.append(ListingDC(movie=movie_title, time=time_object,
                                          venue='Omniplex Dublin Rathmines', maxx=maxx))


from pprint import pprint

pprint(listings)

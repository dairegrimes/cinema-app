from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime
import time_common
import requests
from dataclasses import dataclass
from src.backend.db.models.listing import Listing
from src.backend.db.models.movie import Movie
from src.backend.db.models.venue import Venue

from src.backend.db.repo.db_setup import session_maker


@dataclass
class ListingDC:
    movie: str
    time: datetime
    venue: str
    maxx: bool


def get_time(data_date: str, time: str) -> datetime:
    day, month, year = data_date.split('-')
    hour, minute = time.split(':')
    return time_common.get_datetime(int(year), int(month), int(day), int(hour), int(minute))


page_to_scrape = requests.get('https://www.omniplex.ie/cinema/dublin-rathmines')
soup = BeautifulSoup(page_to_scrape.text, "html.parser")
movies = soup.find('div', class_='OMP_mainContainer')
date_times = []
listings = []
movies_list = set()
movie_to_listing_mapping = defaultdict(list)
for movie in movies.find_all('div', class_='OMP_splitSection'):
    button = movie.find(class_="OMP_buttonSelection")
    if button:
        movie_title = movie.find("h3", class_="OMP_inlineBlock").get_text()
        time_divs = movie.find_all("div", class_="OMP_listingDate")
        for div in time_divs:
            grouped_times = []
            data_date = div.get("data-date")
            for a in div.find_all("a", class_="OMP_buttonSelection"):
                time = a.get_text(strip=True)
                if 'SoldOut' in time:
                    continue
                time_object = get_time(data_date, time)
                maxx = True if "maxx" in a.get("href", "") else False
                movies_list.add(movie_title)
                listings.append(ListingDC(movie=movie_title, time=time_object,
                                          venue='Omniplex Dublin Rathmines', maxx=maxx))

session = session_maker()


def add_movie(listing):
    movie = session.query(Movie).filter_by(name=listing.movie.name).scalar()
    if not movie:
        movie_object = Movie(name=listing.movie.name)
        session.add(movie_object)
        session.commit()
        return session.query(Movie).filter_by(name=listing.movie.name).scalar()
    return movie


for movie_name in movies_list:
    movie = session.query(Movie).filter_by(name=movie_name).scalar()
    if not movie:
        session.add(Movie(name=movie_name))
        session.commit()

id_to_movie_mapping = {movie.name: movie for movie in session.query(Movie).all()}
venue = session.query(Venue).filter_by(name='Omniplex Dublin Rathmines').scalar()

current_ids = set()


def create_listing_id(listing_id):
    i = 1
    while True:
        new_listing_id = f"{listing_id}-{i}"
        if new_listing_id not in current_ids:
            return new_listing_id
        i += 1


for listing in listings:
    movie = id_to_movie_mapping[listing.movie]
    listing_object = Listing(movie=movie,
                             time=listing.time,
                             venue=venue,
                             maxx=listing.maxx)
    listing_id = f"{movie.id}-{venue.id}-{listing_object.time}"
    if listing_id not in current_ids:
        current_ids.add(listing_id)
    else:
        listing_id = create_listing_id(listing_id)
        current_ids.add(listing_id)
    listing_object.listing_id = listing_id
    session.add(listing_object)
session.commit()

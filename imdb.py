import requests
from bs4 import BeautifulSoup
from googlesearch import search
import re


pattern = r'tt\d+'


def get_imdb_rating(film):
    site = 'imdb.com'
    query = f"{film} site:{site}"
    for result in search(query, num_results=5):
        if "imdb.com/title" in result:
            match = re.search(pattern, result)
            imdb_id = match.group()
            result = f'https://www.imdb.com/title/{imdb_id}'

            break
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(result, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        rating_div = soup.find('div', {'data-testid': 'hero-rating-bar__aggregate-rating__score'})
        return rating_div.text


def get_rotten_tamatoes(film):
    site = 'https://www.rottentomatoes.com/search?search='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(f"{site}{film}", headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    media_row = soup.find_all('search-page-media-row')


    link = [a['href'] for a in media_row.find_all('a', href=True)]

    print(link)
    exit(0)
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        criticsScore = soup.find('rt-text', {'slot': 'criticsScore'})
        audienceScore = soup.find('rt-text', {'slot': 'audienceScore'})
        return {'criticsScore': criticsScore.text, 'audienceScore': audienceScore.text}


films = movies = [
    "The Shawshank Redemption",
    "The Godfather",
    "The Dark Knight",
    "The Godfather Part II",
    "12 Angry Men",
    "Schindler's List",
    "The Lord of the Rings: The Return of the King",
    "Pulp Fiction",
    "The Good, the Bad and the Ugly",
    "Forrest Gump",
    "Fight Club",
    "Inception",
    "The Lord of the Rings: The Fellowship of the Ring",
    "Star Wars: Episode V - The Empire Strikes Back",
    "The Matrix",
    "Goodfellas",
    "One Flew Over the Cuckoo's Nest",
    "Seven Samurai",
    "Se7en",
    "The Silence of the Lambs",
    "City of God",
    "It's a Wonderful Life",
    "Saving Private Ryan",
    "Life Is Beautiful",
    "The Green Mile",
    "Interstellar",
    "Star Wars: Episode IV - A New Hope",
    "Parasite",
    "The Lion King",
    "The Usual Suspects",
    "Spirited Away",
    "Harakiri",
    "The Pianist",
    "Gladiator",
    "The Departed",
    "Back to the Future",
    "Terminator 2: Judgment Day",
    "Whiplash",
    "The Prestige",
    "The Dark Knight Rises",
    "Once Upon a Time in the West",
    "Casablanca",
    "American History X",
    "Psycho",
    "City Lights",
    "Avengers: Infinity War",
    "Modern Times",
    "Coco",
    "The Great Dictator",
    "Django Unchained",
    "The Lives of Others",
    "WALL-E",
    "Sunset Boulevard",
    "Grave of the Fireflies",
    "Avengers: Endgame",
    "Paths of Glory",
    "The Shining",
    "Witness for the Prosecution",
    "The Wolf of Wall Street",
    "Memento",
    "Dr. Strangelove",
    "Alien",
    "Raiders of the Lost Ark",
    "Joker",
    "Oldboy",
    "Braveheart",
    "Toy Story",
    "Amélie",
    "Inglourious Basterds",
    "The Dark Knight Rises",
    "Princess Mononoke",
    "Your Name",
    "WALL-E",
    "Requiem for a Dream",
    "The Hunt",
    "The Truman Show",
    "The Grand Budapest Hotel",
    "A Clockwork Orange",
    "The Big Lebowski",
    "Shutter Island",
    "The Avengers",
    "Batman Begins",
    "Dangal",
    "The Social Network",
    "The Sixth Sense",
    "Zootopia",
    "La La Land",
    "Spider-Man: Into the Spider-Verse",
    "The Incredibles",
    "Up",
    "Finding Nemo",
    "Slumdog Millionaire",
    "Eternal Sunshine of the Spotless Mind",
    "The Imitation Game",
    "Inside Out",
    "The Curious Case of Benjamin Button",
    "The Theory of Everything",
    "Black Swan",
    "The King's Speech"
]
films = ['up']
for film in films:
    print(film)
    print(get_rotten_tamatoes(film))
    print('\n')

import os
import requests

from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Load environment variables from the .env file
load_dotenv()

# Use os.getenv to retrieve the values
API_KEY = os.getenv('LASTFM_API_KEY')
USERNAME = os.getenv('LASTFM_USERNAME')
timeframe = os.getenv('timeframe')
albums_wide = int(os.getenv('albums_wide'))
albums_tall = int(os.getenv('albums_tall'))

ALBUMS_LIMIT = albums_tall * albums_wide

def fetch_top_albums(username, limit, period):
    """Fetches top albums for a Last.fm user."""
    params = {
        'method': 'user.getTopAlbums',
        'user': USERNAME,
        'api_key': API_KEY,
        'format': 'json',
        'limit': ALBUMS_LIMIT,
        'period': timeframe
    }
    response = requests.get('http://ws.audioscrobbler.com/2.0/', params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {'name': album['name'], 'artist': album['artist']['name'], 'url': album['image'][-1]['#text']}
            for album in data['topalbums']['album']
        ]
    else:
        raise Exception("Error fetching top albums from Last.fm")

def fetch_album_art(album_url):
    """Fetches album art from a URL."""
    response = requests.get(album_url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        raise Exception(f"Error fetching image from {album_url}")

def create_collage(albums, albums_wide, albums_tall):
    """Creates a collage of album arts."""
    if len(albums) < albums_wide * albums_tall:
        raise ValueError("Not enough albums to fill the collage")

    album_size = int(os.getenv('album_size_px'))  # Size of each album cover in pixels
    collage_width = album_size * albums_wide
    collage_height = album_size * albums_tall

    collage = Image.new('RGB', (collage_width, collage_height))
    x_offset = 0
    y_offset = 0

    for i, album in enumerate(albums[:albums_wide * albums_tall]):
        try:
            album_art = fetch_album_art(album['url']).resize((album_size, album_size))
            collage.paste(album_art, (x_offset, y_offset))
            x_offset += album_size
            if (i + 1) % albums_wide == 0:
                x_offset = 0
                y_offset += album_size
        except Exception as e:
            print(f"An error occurred: {e}")

    collage.save(f"{albums_wide}x{albums_tall}_{timeframe}_collage.png")

top_albums = fetch_top_albums(USERNAME, albums_wide * albums_tall, timeframe)
create_collage(top_albums, albums_wide, albums_tall)

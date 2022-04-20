import datetime as dt
import base64
import requests

from urllib.parse import urlencode
from urllib.parse import urlparse


class AccessToken:
    def __init__(self, access_token: str, token_type: str, expires_in: float):
        self.token = access_token
        self.token_type = token_type
        self.expires = dt.datetime.now() + dt.timedelta(seconds=expires_in)

    @staticmethod
    def from_json(data):
        return AccessToken(data["access_token"],
                           data["token_type"],
                           data["expires_in"])

    def is_expired(self):
        return dt.datetime.now() > self.expires


class Track:
    def __init__(self, spotify_track: dict):
        self.track = spotify_track

    def get_thumbnail_url(self) -> str:
        return self.track["video_thumbnail"]["url"]

    def get_duration_ms(self) -> int:
        return self.track["track"]["duration_ms"]

    def get_duration_s(self) -> int:
        return self.track["track"]["duration_ms"] // 1000

    def get_filename(self) -> str:
        return f"{', '.join(self.get_artist_names())} - {self.get_name()}"

    def get_name(self) -> str:
        return self.track["track"]["name"]

    def get_album_name(self) -> str:
        return self.track["track"]["album"]["name"]

    def get_artist_names(self) -> list[str]:
        artists = []
        for artist in self.track["track"]["artists"]:
            artists.append(artist["name"])
        return artists

    def get_album_artist_names(self) -> list[str]:
        artists = []
        for artist in self.track["track"]["album"]["artists"]:
            artists.append(artist["name"])
        return artists


class Spotify:
    def __init__(self, spotify_response: dict):
        self.spotify = spotify_response

    def get_playlist_name(self) -> str:
        return self.spotify["name"]

    def get_generator_tracks(self):
        for track in self.spotify["tracks"]["items"]:
            yield Track(track)


class SpotifyAPI:

    URL_TOKEN = "https://accounts.spotify.com/api/token"
    URL_SEARCH = "https://api.spotify.com/v1/search"

    TOKEN_DATA = {"grant_type": "client_credentials"}

    def __init__(self, client_id: str, client_secret: str):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.CLIENT_CREDS = f"{client_id}:{client_secret}"
        self.CLIENT_CREDS_64 = (base64.b64encode(
            self.CLIENT_CREDS.encode()
        )).decode()
        self.HEADERS_AUTHORIZE = {"Authorization":
                                      f"basic {self.CLIENT_CREDS_64}"}

        self.access_token = self._authorize()

        self.HEADERS_SEARCH = {"Authorization":
                                   f"{self.access_token.token_type} "
                                   f"{self.access_token.token}"}

    def _authorize(self) -> AccessToken:
        response = requests.post(self.URL_TOKEN,
                                 data=self.TOKEN_DATA,
                                 headers=self.HEADERS_AUTHORIZE)
        if response.status_code not in range(200, 299):
            raise Exception(f"could not authorizse STATUS: {response.status_code}")
        return AccessToken.from_json(response.json())

    def search(self, query: str, search_type: str) -> dict:
        data = urlencode({"q": query, "type": search_type})
        url = f"{self.URL_SEARCH}?{data}"
        return requests.get(url, headers=self.HEADERS_SEARCH).json()

    def get_playlist(self, url: str) -> dict:
        playlist_id = urlparse(url).path.split("/")[-1]
        return requests.get(
            f"https://api.spotify.com/v1/playlists/{playlist_id}",
            headers=self.HEADERS_SEARCH
        ).json()

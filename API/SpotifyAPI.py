import datetime as dt
import base64
import requests
from itertools import count


from urllib.parse import urlparse
from Downloader import replace_illegal_chars


TYPE_PLAYLIST = "playlist"
TYPE_ALBUM = "album"
TYPE_TRACK = "track"


def is_url_playlist(url: str) -> bool:
    return True if "playlist" in urlparse(url).path else False


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


class TrackPlaylist:
    def __init__(self, spotify_track: dict, id: int):
        self.track = spotify_track
        self.id = id

    def get_album_thumbnail_url(self) -> str:
        return self.track["track"]["album"]["images"][0]["url"]

    def get_duration_ms(self) -> int:
        return self.track["track"]["duration_ms"]

    def get_duration_s(self) -> int:
        return round(self.track["track"]["duration_ms"] / 1000)

    def get_filename(self) -> str:
        return replace_illegal_chars(
            f"{self.get_name()} - {', '.join(self.get_artist_names())}"
        )

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


class TrackAlbum:
    def __init__(self, spotify_track: dict, album: dict, id: int):
        self.track = spotify_track
        self.album = album
        self.id = id

    def get_album_thumbnail_url(self) -> str:
        return self.album["images"][0]["url"]

    def get_duration_ms(self) -> int:
        return self.track["duration_ms"]

    def get_duration_s(self) -> int:
        return round(self.track["duration_ms"] / 1000)

    def get_filename(self) -> str:
        return replace_illegal_chars(
            f"{self.get_name()} - {', '.join(self.get_artist_names())}"
        )

    def get_name(self) -> str:
        return self.track["name"]

    def get_album_name(self) -> str:
        return self.album["name"]

    def get_artist_names(self) -> list[str]:
        artists = []
        for artist in self.track["artists"]:
            artists.append(artist["name"])
        return artists

    def get_album_artist_names(self) -> list[str]:
        artists = []
        for artist in self.album["artists"]:
            artists.append(artist["name"])
        return artists


class TrackSingle:
    def __init__(self, spotify_track: dict, id: int):
        self.track = spotify_track
        self.id = id

    def get_album_thumbnail_url(self) -> str:
        return self.track["album"]["images"][0]["url"]

    def get_duration_ms(self) -> int:
        return self.track["duration_ms"]

    def get_duration_s(self) -> int:
        return round(self.track["duration_ms"] / 1000)

    def get_filename(self) -> str:
        return replace_illegal_chars(
            f"{self.get_name()} - {', '.join(self.get_artist_names())}"
        )

    def get_name(self) -> str:
        return self.track["name"]

    def get_album_name(self) -> str:
        return self.track["album"]["name"]

    def get_artist_names(self) -> list[str]:
        artists = []
        for artist in self.track["artists"]:
            artists.append(artist["name"])
        return artists

    def get_album_artist_names(self) -> list[str]:
        artists = []
        for artist in self.track["album"]["artists"]:
            artists.append(artist["name"])
        return artists


class Spotify:
    def __init__(self, spotify_response: dict, type: str, id: int, album=None):
        self.spotify = spotify_response
        self.album = album
        self.id = id
        self.type = type

    def get_name(self) -> str:
        if self.type == TYPE_PLAYLIST:
            return self.spotify["name"]
        if self.type == TYPE_ALBUM:
            return self.album["name"]
        if self.type == TYPE_TRACK:
            return self.spotify["name"]

    def get_generator_tracks(self):
        if self.type == TYPE_PLAYLIST:
            for track, id in zip(self.spotify["tracks"]["items"],
                                 count(start=self.id)):
                yield TrackPlaylist(track, id)
        if self.type == TYPE_ALBUM:
            for track, id in zip(self.spotify["items"], count(start=self.id)):
                yield TrackAlbum(track, self.album)
        if self.type == TYPE_TRACK:
            yield TrackSingle(self.spotify, self.id)

    def __len__(self):
        if self.type == TYPE_PLAYLIST:
            return len(self.spotify["tracks"]["items"])
        if self.type == TYPE_ALBUM:
            return len(self.spotify["items"])
        if self.type == TYPE_TRACK:
            return 1


class SpotifyAPI:

    URL_TOKEN = "https://accounts.spotify.com/api/token"
    URL_SEARCH = "https://api.spotify.com/v1/search"

    TOKEN_DATA = {"grant_type": "client_credentials"}

    def __init__(self, client_id: str, client_secret: str, track_id: int):
        self.track_id = track_id
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

    def get_tracks(self, url: str) -> Spotify:
        if "playlist" in url:
            return self.get_playlist(url)
        if "album" in url:
            return self.get_album(url)
        if "track" in url:
            return self.get_track(url)
        raise Exception("Could not get tracks from Spotify")

    def get_track(self, url: str) -> Spotify:
        track_id = urlparse(url).path.split("/")[-1]
        return Spotify(requests.get(
            f"https://api.spotify.com/v1/tracks/{track_id}",
            headers=self.HEADERS_SEARCH
        ).json(), TYPE_TRACK, self.track_id)

    def get_playlist(self, url: str) -> Spotify:
        playlist_id = urlparse(url).path.split("/")[-1]
        return Spotify(requests.get(
            f"https://api.spotify.com/v1/playlists/{playlist_id}",
            headers=self.HEADERS_SEARCH
        ).json(), TYPE_PLAYLIST, self.track_id)

    def get_album(self, url: str) -> Spotify:
        album_id = urlparse(url).path.split("/")[-1]
        tracks = requests.get(
            f"https://api.spotify.com/v1/albums/{album_id}/tracks",
            headers=self.HEADERS_SEARCH
        ).json()
        album = requests.get(
            f"https://api.spotify.com/v1/albums/{album_id}",
            headers=self.HEADERS_SEARCH
        ).json()
        return Spotify(tracks, TYPE_ALBUM, self.track_id, album=album)

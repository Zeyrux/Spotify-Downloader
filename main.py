import datetime as dt
import base64
import os

from urllib.parse import urlencode
import spotipy
import requests


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
                                      f"Basic {self.CLIENT_CREDS_64}"}

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

    def search(self, query: str, search_type: str):
        data = urlencode({"q": query, "type": search_type})
        url = f"{self.URL_SEARCH}?{data}"
        r = requests.get(url, headers=self.HEADERS_SEARCH)
        return r


def get_client_id_and_secret(path="client.txt") -> tuple:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    return tuple(open(path, "r").read().split("\n"))


def main():
    client_id, client_secret = get_client_id_and_secret()
    print(SpotifyAPI(client_id, client_secret).search("Remedy", "track").json())


if __name__ == '__main__':
    main()

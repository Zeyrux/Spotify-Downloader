import datetime as dt
import base64

import spotipy
import requests

CLIENT_ID = "49a5b55f4d6c4ef2973e5452689d7035"
CLIENT_SECRET = "9aafe4d664ad41cf8ebe9c6e3e2768e2"


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
    def __init__(self, client_id: str, client_secret: str):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.TOKEN_URL = "https://accounts.spotify.com/api/token"
        self.CLIENT_CREDS = f"{client_id}:{client_secret}"
        self.CLIENT_CREDS_64 = (base64.b64encode(
            self.CLIENT_CREDS.encode()
        )).decode()
        self.TOKEN_HEADERS = {"Authorization": f"Basic {self.CLIENT_CREDS_64}"}
        self.TOKEN_DATA = {"grant_type": "client_credentials"}

        self.access_token = self._authorize()

    def _authorize(self) -> AccessToken:
        response = requests.post(self.TOKEN_URL,
                                 data=self.TOKEN_DATA,
                                 headers=self.TOKEN_HEADERS)
        if response.status_code not in range(200, 299):
            raise Exception(f"could not authorizse STATUS: {response.status_code}")
        return AccessToken.from_json(response.json())

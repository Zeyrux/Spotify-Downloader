import time
from itertools import count

from GUI.Exceptions_and_layout import create_exit_exception,\
    create_song_not_found_exception

from googleapiclient.errors import HttpError
import pytube

GET_BEST_SONGS_ARGS = [
    {
        "max_results": 3,
        "max_duration_difference": 5,
        "name_intitle": False,
        "artists_intitle": False
    }, {
        "max_results": 10,
        "max_duration_difference": 10,
        "name_intitle": False,
        "artists_intitle": False
    }, {
        "max_results": 10,
        "max_duration_difference": 15,
        "name_intitle": False,
        "artists_intitle": False
    }, {
        "max_results": 10,
        "max_duration_difference": 30,
        "name_intitle": False,
        "artists_intitle": False,
        "search_artists": False
    }
]


class YoutubeAPI:
    def __init__(self, yt_apps: "YoutubeAppsBuilder"):
        self.yt_apps = yt_apps

    def _search_tracks_youtube(self, args) -> dict:
        for i in count():
            try:
                if i == round(len(self.yt_apps) * 1.5):
                    create_exit_exception("MAX QUOTA REACHED!\nPlease add more"
                                          " Api´s or wait some time")
                a = self.yt_apps.get_app().search().list(part="snippet",
                                                         **args).execute()
                return a
            except HttpError:
                time.sleep(0.25)

    def _get_best_song(self,
                       track,
                       order: str,
                       max_results=10,
                       max_duration_difference=15,
                       name_intitle=True,
                       artists_intitle=True,
                       search_artists=True) -> pytube.YouTube:
        # define args for search
        q = f"({'intitle:' if name_intitle else ''}{track.get_name()})"
        if search_artists:
            for artist in track.get_artist_names():
                q += f"({'intitle:' if artists_intitle else ''}{artist})"
        args = {"q": q,
                "maxResults": max_results,
                "order": order}

        # get best track
        tracks_found = self._search_tracks_youtube(args)

        for track_found in tracks_found["items"]:
            url = f"https://www.youtube.com/watch?v=" \
                  f"{track_found['id']['videoId']}"
            track_pytube = pytube.YouTube(url)
            if track.get_duration_s() - max_duration_difference \
                    < track_pytube.length \
                    < track.get_duration_s() + max_duration_difference:
                return track_pytube

    def search_song(self,
                    track,
                    order="viewCount") -> pytube.YouTube:
        # get best song
        for args in GET_BEST_SONGS_ARGS:
            track_pyt = self._get_best_song(track, order, **args)
            if track_pyt is not None:
                return track_pyt

        # if nothing was found raise exception
        create_song_not_found_exception(track.get_name())

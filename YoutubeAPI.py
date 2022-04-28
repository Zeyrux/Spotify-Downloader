from googleapiclient.discovery import build
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
        "max_duration_difference": 15,
        "name_intitle": False,
        "artists_intitle": False,
        "search_artists": False
    }
]


class YoutubeAPI:
    def __init__(self, api_key):
        self.API_KEY = api_key
        self.youtube = build("youtube", "v3", developerKey=self.API_KEY)

    def _get_best_song(self,
                       track: "Track",
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
        tracks_found = self.youtube.search().list(part="snippet",
                                                  **args).execute()
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
        raise Exception("Could´t find any song at youtube")

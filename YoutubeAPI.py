from googleapiclient.discovery import build
import pytube

GET_BEST_SONGS_ARGS = [
    {},
    {"artists_intitle": False},
    {"artists_intitle": False, "name_intitle": False},
    {"artists_intitle": False, "name_intitle": False, "search_artists": False}
]


class YoutubeAPI:
    def __init__(self, api_key):
        self.API_KEY = api_key
        self.youtube = build("youtube", "v3", developerKey=self.API_KEY)

    def _get_best_song(self,
                       track: "Track",
                       max_results: int,
                       order: str,
                       max_duration_difference: int,
                       name_intitle=True,
                       search_artists=True,
                       artists_intitle=True) -> pytube.YouTube:
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
                    track: "Track",
                    max_results=30,
                    order="viewCount",
                    max_duration_difference=30) -> pytube.YouTube:
        # get best song
        for args in GET_BEST_SONGS_ARGS:
            track_pyt = self._get_best_song(track, max_results,
                                            order, max_duration_difference,
                                            **args)
            if track_pyt is not None:
                return track_pyt

        # if nothing was found raise exception
        raise Exception("Could´t find any song at youtube")

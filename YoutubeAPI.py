from googleapiclient.discovery import build
import pytube


class YoutubeAPI:
    def __init__(self, api_key):
        self.API_KEY = api_key
        self.youtube = build("youtube", "v3", developerKey=self.API_KEY)

    def search_song(self,
                    track_name: str,
                    artists: list = None,
                    video_duration: int = None,
                    max_results = 20
                    ) -> tuple[pytube.YouTube, dict]:
        q = f"(intitle:{track_name})"
        if artists is not None:
            for artist in artists:
                q += f"(intitle:{artist})"
        args = {"q": q, "maxResults": max_results}
        tracks = self.youtube.search().list(part="snippet", **args).execute()
        for track in tracks["items"]:
            track_id = track["id"]["videoId"]
            url = f"https://www.youtube.com/watch?v={track_id}"
            track_object = pytube.YouTube(url)
            if video_duration - 5 < track_object.length < video_duration + 5:
                return track_object, track

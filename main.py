import os

from SpotifyAPI import SpotifyAPI
from YoutubeAPI import YoutubeAPI


def get_spotify_client_id_and_secret(path="spotify_api_keys.txt") -> tuple:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    return tuple(open(path, "r").read().split("\n"))


def get_youtube_api_key(path="youtube_api_keys.txt"):
    return open(path, "r").read()


def main():
    playlist_url = input("Playlist URL: ")
    playlist_url = "https://open.spotify.com/playlist/0M5W3EwBG1ewC2ky7ND034?si=f112f80f11004560"

    spotify_api_id, spotify_api_secret = get_spotify_client_id_and_secret()
    spotify_response = SpotifyAPI(
        spotify_api_id,
        spotify_api_secret
    ).get_playlist(playlist_url)

    youtube_api_key = get_youtube_api_key()
    spotify_tracks = spotify_response["tracks"]["items"]
    for spotify_track in spotify_tracks:
        duration = spotify_track["track"]["duration_ms"] // 1000
        track_name = spotify_track["track"]["name"]
        artists = spotify_track["track"]["album"]["artists"]
        artists_name = []
        for artist in artists:
            artists_name.append(artist["name"])

        pytube_track, _ = YoutubeAPI(youtube_api_key).search_song(track_name,
                                                                  artists_name,
                                                                  duration)
        # print(pt_object.thumbnail_url)
        # break


if __name__ == '__main__':
    main()

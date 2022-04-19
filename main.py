import os
import pathlib

from SpotifyAPI import SpotifyAPI
from YoutubeAPI import YoutubeAPI
from donwloader import download_song, replace_illegal_chars


PATH_DOWNLOAD = os.path.join(os.path.expanduser("~"), "downloads")


def get_spotify_client_id_and_secret(path="spotify_api_keys.txt") -> tuple:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    return tuple(open(path, "r").read().split("\n"))


def get_youtube_api_key(path="youtube_api_keys.txt"):
    return open(path, "r").read()


def main():
    playlist_url = input("Playlist URL: ")
    playlist_url = "https://open.spotify.com/playlist/0M5W3EwBG1ewC2ky7ND034?si=db824fd9c6034527"

    spotify_api_id, spotify_api_secret = get_spotify_client_id_and_secret()
    spotify_response = SpotifyAPI(
        spotify_api_id,
        spotify_api_secret
    ).get_playlist(playlist_url)

    youtube_api_key = get_youtube_api_key()
    spotify_tracks = spotify_response["tracks"]["items"]

    download_path_with_dir = os.path.join(
        PATH_DOWNLOAD,
        replace_illegal_chars(spotify_response["name"])
    )
    pathlib.Path(os.path.join(download_path_with_dir)).mkdir(exist_ok=True,
                                                             parents=True)

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
        download_song(pytube_track, download_path_with_dir)


if __name__ == '__main__':
    main()

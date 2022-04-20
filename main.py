import os
import pathlib
import shutil

from SpotifyAPI import SpotifyAPI, Spotify
from YoutubeAPI import YoutubeAPI
from Downloader import Downloader, replace_illegal_chars, PATH_TEMP


PATH_DOWNLOAD = os.path.join(os.path.expanduser("~"), "downloads")


def get_spotify_client_id_and_secret(path="spotify_api_keys.txt") -> tuple:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    return tuple(open(path, "r").read().split("\n"))


def get_youtube_api_key(path="youtube_api_keys.txt"):
    return open(path, "r").read()


def main():
    playlist_url = input("Playlist URL: ")

    # get keys
    spotify_api_id, spotify_api_secret = get_spotify_client_id_and_secret()
    youtube_api_key = get_youtube_api_key()

    # get playlist
    print("Get playlist")
    spotify_response = SpotifyAPI(
        spotify_api_id,
        spotify_api_secret
    ).get_playlist(playlist_url)
    spotify = Spotify(spotify_response)

    # declare download path and create if necessary
    download_path_with_dir = os.path.join(
        PATH_DOWNLOAD,
        replace_illegal_chars(spotify.get_playlist_name())
    )
    pathlib.Path(os.path.join(download_path_with_dir)).mkdir(exist_ok=True,
                                                             parents=True)
    # iterate throw each track and download it
    for track in spotify.get_generator_tracks():
        # search for song
        pytube_track, _ = YoutubeAPI(
            youtube_api_key
        ).search_song(track.get_name(),
                      track.get_artist_names(),
                      track.get_duration_s())
        print(f"\nFound Song: {pytube_track.title}: {pytube_track.watch_url}")
        # download song
        Downloader(pytube_track,
                   track,
                   download_path_with_dir
                   ).download_song()
        # move to downloads
        src = os.path.join(PATH_TEMP, track.get_filename() + ".mp3")
        target = os.path.join(PATH_DOWNLOAD,
                              spotify.get_playlist_name(),
                              track.get_filename() + ".mp3")
        shutil.move(src, target)


if __name__ == '__main__':
    main()

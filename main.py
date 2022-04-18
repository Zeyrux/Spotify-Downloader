import os

from SpotifyAPI import SpotifyAPI


def get_client_id_and_secret(path="client.txt") -> tuple:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    return tuple(open(path, "r").read().split("\n"))


def main():
    client_id, client_secret = get_client_id_and_secret()
    a = SpotifyAPI(client_id, client_secret).get_playlist("https://open.spotify.com/playlist/0M5W3EwBG1ewC2ky7ND034?si=f112f80f11004560")
    b = a["tracks"]["items"]
    for c in b:
        print(f'{c["track"]["name"]}')
        print(f'{c["track"]["external_urls"]["spotify"]}')
        artists = c["track"]["album"]["artists"]
        print("Artists:")
        for artist in artists:
            print(f'\t{artist["name"]}')
        print()


if __name__ == '__main__':
    main()

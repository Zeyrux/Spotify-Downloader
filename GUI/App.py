import sys
import os
import pathlib
import shutil
import multiprocessing as mp

from API.SpotifyAPI import SpotifyAPI
from API.YoutubeAPI import YoutubeAPI
from Downloader import Downloader, replace_illegal_chars, PATH_TEMP
from YoutubeAppsBuilder import YoutubeAppsBuilder

from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QApplication,
    QProgressBar,
    QWidget
)


PATH_DOWNLOAD = os.path.join(os.path.expanduser("~"), "downloads")


def get_spotify_client_id_and_secret(path="API\\spotify_api_keys.txt") -> tuple:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    return tuple(open(path, "r").read().split("\n"))


def download_loop(track,
                  spotify: "Spotify",
                  yt_apps: "YoutubeAppsBuilder",
                  download_path_with_dir: str,
                  out_func):
    # search for song
    pytube_track = YoutubeAPI(
        yt_apps
    ).search_song(track)
    print("found song")
    # download song
    Downloader(pytube_track,
               track,
               download_path_with_dir
               ).download_song()
    # move to downloads
    src = os.path.join(PATH_TEMP, track.get_filename() + ".mp3")
    target = os.path.join(PATH_DOWNLOAD,
                          spotify.get_name(),
                          track.get_filename() + ".mp3")
    shutil.move(src, target)


class App(QMainWindow):

    spotify: "Spotify" = None
    download_path_with_dir: str = None
    spotify_api_id, spotify_api_secret = get_spotify_client_id_and_secret()
    yt_apps = YoutubeAppsBuilder()
    progress_bars = {}

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Downloader ⭳")

        # url input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Link")
        self.download_button = QPushButton("⭳")
        self.download_button.clicked.connect(self.get_tracks)

        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.url_input)
        self.input_layout.addWidget(self.download_button)
        self.input_widget = QWidget()
        self.input_widget.setLayout(self.input_layout)

        # final layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.input_widget)
        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

    def get_tracks(self):
        url = self.url_input.text()
        self.spotify = SpotifyAPI(
            self.spotify_api_id,
            self.spotify_api_secret
        ).get_tracks(url)

        # declare download path and create if necessary
        self.download_path_with_dir = os.path.join(
            PATH_DOWNLOAD,
            replace_illegal_chars(self.spotify.get_name())
        )
        pathlib.Path(
            os.path.join(self.download_path_with_dir)
        ).mkdir(exist_ok=True, parents=True)

        self.create_progress_bars()
        self.start_downloading()

    def start_downloading(self):
        # iterate through each track and add process that download it
        procs = []
        for track in self.spotify.get_generator_tracks():
            procs.append(mp.Process(
                target=download_loop,
                args=(track, self.spotify, self.yt_apps,
                      self.download_path_with_dir, self.out_func),
                daemon=True
            ))
        # start downloading
        for proc in procs:
            proc.start()
            break

    def create_progress_bars(self):
        for track in self.spotify.get_generator_tracks():
            progress_bar = QProgressBar()
            progress_bar.setMaximum(4)
            progress_bar.setFormat(track.get_filename())
            progress_bar.setValue(1)
            self.layout.addWidget(progress_bar)
            self.progress_bars[id(track)] = progress_bar

    def out_func(self, track):
        print(self.progress_bars.get(id(track)).value())


def create_app():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    app.setStyle("Fusion")
    app.exec()

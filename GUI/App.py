import sys
import os
import pathlib
import shutil
import multiprocessing as mp
import threading

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


PATH_STYLESHEET = os.path.join("Styles", "style.css")
STYLE_APP = "Fusion"
STYLESHEET = open(PATH_STYLESHEET, "r").read()
PATH_DOWNLOAD = os.path.join(os.path.expanduser("~"), "downloads")


def get_spotify_client_id_and_secret(path="API\\spotify_api_keys.txt") -> tuple:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    return tuple(open(path, "r").read().split("\n"))


def download_loop(track,
                  spotify: "Spotify",
                  yt_apps: "YoutubeAppsBuilder",
                  download_path_with_dir: str,
                  pipe: "mp.connection.PipeConnection"):
    # search for song
    pytube_track = YoutubeAPI(
        yt_apps
    ).search_song(track)
    pipe.send(track.id)
    # download song
    Downloader(pytube_track,
               track,
               download_path_with_dir,
               pipe
               ).download_song()
    pipe.send(track.id)
    # move to downloads
    src = os.path.join(PATH_TEMP, track.get_filename() + ".mp3")
    target = os.path.join(PATH_DOWNLOAD,
                          spotify.get_name(),
                          track.get_filename() + ".mp3")
    shutil.move(src, target)
    pipe.send(track.id)


class App(QMainWindow):

    spotify: "Spotify" = None
    download_path_with_dir: str = None
    spotify_api_id, spotify_api_secret = get_spotify_client_id_and_secret()
    yt_apps = YoutubeAppsBuilder()
    progress_bars = {}
    pipes = {}
    cur_track_id = 0

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Downloader ⭳")
        self.clear_temp()

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

        self.setStyleSheet(STYLESHEET)
        self.setCentralWidget(self.widget)

    def get_tracks(self):
        url = self.url_input.text()
        self.spotify = SpotifyAPI(
            self.spotify_api_id,
            self.spotify_api_secret,
            self.cur_track_id
        ).get_tracks(url)
        self.cur_track_id += len(self.spotify)

        # declare download path and create if necessary
        self.download_path_with_dir = os.path.join(
            PATH_DOWNLOAD,
            replace_illegal_chars(self.spotify.get_name())
        )
        pathlib.Path(
            os.path.join(self.download_path_with_dir)
        ).mkdir(exist_ok=True, parents=True)

        self.create_progress_bars()
        # self.start_downloading()

    def start_downloading(self):
        # iterate through each track and add process that download it
        procs = []
        for track in self.spotify.get_generator_tracks():
            parent_conn, child_conn = mp.Pipe()
            procs.append(mp.Process(
                target=download_loop,
                args=(track, self.spotify, self.yt_apps,
                      self.download_path_with_dir, child_conn),
                daemon=True
            ))
            threading.Thread(target=self.reply_pipe, args=(parent_conn,),
                             daemon=True).start()
        # start downloading
        for proc in procs:
            proc.start()

    def reply_pipe(self, parent_conn: "mp.connection.PipeConnection"):
        for i in range(2, 9):
            self.progress_bars[parent_conn.recv()].setValue(i)

    def create_progress_bars(self):
        for track in self.spotify.get_generator_tracks():
            progress_bar = QProgressBar()
            progress_bar.setMaximum(8)
            progress_bar.setFormat(track.get_filename())
            progress_bar.setValue(1)
            self.layout.addWidget(progress_bar)
            self.progress_bars[track.id] = progress_bar

    def clear_temp(self):
        pathlib.Path(PATH_TEMP).mkdir(parents=True, exist_ok=True)
        for file in os.listdir(PATH_TEMP):
            os.remove(os.path.join(PATH_TEMP, file))


def create_app():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    app.setStyle(STYLE_APP)
    app.exec()

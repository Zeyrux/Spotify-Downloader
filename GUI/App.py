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
from GUI.Exceptions_and_layout import LayoutProgressBar

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QApplication,
    QWidget
)

PATH_STYLESHEET = os.path.join("Styles", "style.css")
STYLE_APP = "Fusion"
STYLESHEET = open(PATH_STYLESHEET, "r").read()
PATH_DOWNLOAD = os.path.join(os.path.expanduser("~"), "downloads")


def get_spotify_client_id_and_secret(
        path="API\\spotify_api_keys.txt") -> tuple:
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


class Worker(QThread):
    signal_increase_track_id = pyqtSignal(object)
    signal_create_progress_bar = pyqtSignal(object)
    signal_update_progress_bar = pyqtSignal(object)
    signal_finish = pyqtSignal(object)
    download_path_with_dir: str = ""
    spotify: "Spotify"

    def __init__(self, spotfiy_api: SpotifyAPI,
                 url: str,
                 yt_apps: "YoutubeAppsBuilder"):
        super().__init__()
        self.api = spotfiy_api
        self.url = url
        self.yt_apps = yt_apps

    def run(self):
        self.get_tracks()

    def connect_increase_track_id(self, fn):
        self.signal_increase_track_id.connect(fn)

    def connect_create_progress_bar(self, fn):
        self.signal_create_progress_bar.connect(fn)

    def connect_update_progress_bar(self, fn):
        self.signal_update_progress_bar.connect(fn)

    def connect_finish(self, fn):
        self.signal_finish.connect(fn)

    def reply_pipe(self, parent_conn: "mp.connection.PipeConnection"):
        for i in range(2, 8):
            self.signal_update_progress_bar.emit(parent_conn.recv())
        track_id = parent_conn.recv()
        self.signal_update_progress_bar.emit(track_id)
        self.signal_finish.emit(track_id)

    def get_tracks(self):
        self.spotify = self.api.get_tracks(self.url)
        self.signal_increase_track_id.emit(len(self.spotify))

        # declare download path and create if necessary
        self.download_path_with_dir = os.path.join(
            PATH_DOWNLOAD,
            replace_illegal_chars(self.spotify.get_name())
        )
        pathlib.Path(
            os.path.join(self.download_path_with_dir)
        ).mkdir(exist_ok=True, parents=True)

        # create progress bars
        for track in self.spotify.get_generator_tracks():
            self.signal_create_progress_bar.emit(track)

        self.start_downloading()

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


def clear_temp():
    pathlib.Path(PATH_TEMP).mkdir(parents=True, exist_ok=True)
    for file in os.listdir(PATH_TEMP):
        os.remove(os.path.join(PATH_TEMP, file))


class App(QMainWindow):

    workers: list[Worker] = []
    spotify_api_id, spotify_api_secret = get_spotify_client_id_and_secret()
    yt_apps = YoutubeAppsBuilder()
    cur_track_id = 0

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Downloader ⭳")
        clear_temp()

        # url input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Link")
        self.download_button = QPushButton("⭳")
        self.download_button.clicked.connect(self.start_get_tracks)

        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.url_input)
        self.input_layout.addWidget(self.download_button)
        self.input_widget = QWidget()
        self.input_widget.setLayout(self.input_layout)
        self.input_widget.setMaximumHeight(self.screen().size().height() // 15)
        self.input_widget.setMinimumHeight(self.screen().size().height() // 15)

        # final layout
        self.app_layout = QVBoxLayout()
        self.app_layout.addWidget(self.input_widget)
        self.widget = QWidget()
        self.widget.setLayout(self.app_layout)

        self.setStyleSheet(STYLESHEET)
        self.setCentralWidget(self.widget)
        #
        # # set fixed size
        # self.input_width = self.width()
        # self.input_height = self.screen().size().height() // 15
        # self.widget.setMinimumHeight(self.input_height)
        # self.widget.setMaximumHeight(self.input_height)
        # self.setFixedSize(self.input_width, self.input_height)

        # progress bars
        self.progress_bars = LayoutProgressBar(
            self,
            self.input_widget.width(),
            self.input_widget.height()
        )
        self.app_layout.addWidget(self.progress_bars)

    def start_get_tracks(self):
        spotify_api = SpotifyAPI(
            self.spotify_api_id,
            self.spotify_api_secret,
            self.cur_track_id
        )
        url = self.url_input.text()

        # create, start, connect worker
        self.workers.append(Worker(spotify_api, url, self.yt_apps))
        self.workers[-1].start()
        self.workers[-1].connect_increase_track_id(self.increase_track_id)
        self.workers[-1].connect_create_progress_bar(
            self.progress_bars.create_progress_bar
        )
        self.workers[-1].connect_update_progress_bar(
            self.progress_bars.update_progressbar
        )
        self.workers[-1].connect_finish(
            self.progress_bars.remove_progressbar
        )

    def increase_track_id(self, val: int):
        self.cur_track_id += val

    # def resize_app(self, progress_bar=None):
    #     if len(self.progress_bars) == 0:
    #         self.setFixedHeight(self.input_height)
    #         return
    #     new_y = self.input_height + self.progress_bars_y
    #     if new_y + self.y() > self.screen().size().height():
    #         y = self.screen().size().height() - self.y() - self.input_height
    #         cnt_progress_bars_per_row = y // self.progress_bars[0].height()
    #         max_rows = math.ceil(len(self.progress_bars)
    #                                    / cnt_progress_bars_per_row)
    #
    #         # create each row
    #         if max_rows == len(self.progress_bars_layouts):
    #             return
    #         for row in range(max_rows):
    #             if self.progress_bars_layouts:
    #                 pass
    #                 # hier weitermachen!!!!!!!!!!!!!!!!!!
    #     self.setFixedHeight(new_y)


def create_app():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    app.setStyle(STYLE_APP)
    app.exec()

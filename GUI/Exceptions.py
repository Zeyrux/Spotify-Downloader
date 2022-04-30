import os
import sys

from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
    QApplication
)


class ExitException(QMainWindow):
    def __init__(self, msg: str):
        super().__init__()
        self.setWindowTitle("Error")

        self.label = QLabel(msg)
        self.button = QPushButton("Exit")
        self.button.clicked.connect(self.kill_parent)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

    def kill_parent(self):
        os.system(f"taskkill  /F /pid {os.getppid()}")


class SongNotFoundException(QMainWindow):
    def __init__(self, song: str):
        super().__init__()
        self.setWindowTitle("Error")

        self.label = QLabel(f"Could not find {song} on youtube")
        self.button = QPushButton("Exit")
        self.button.clicked.connect(self.kill)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

    def kill(self):
        os.system(f"taskkill /F /pid {os.getpid()}")


def create_exit_exception(msg: str):
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ExitException(msg)
    window.show()
    app.exec()


def create_song_not_found_exception(song: str):
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SongNotFoundException(song)
    window.show()
    app.exec()

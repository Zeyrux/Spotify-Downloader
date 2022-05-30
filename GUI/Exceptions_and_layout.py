import os
import sys

from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
    QApplication,
    QGridLayout,
    QProgressBar
)


class CustomProgressBar(QProgressBar):

    pos_x = 0
    pos_y = 0

    def __init__(self, track_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.track_id = track_id

    def set_pos(self, x: int, y: int):
        self.pos_x = x
        self.pos_y = y

    def __str__(self):
        return f"Progressbar(track_id: {self.track_id}, x: {self.pos_x}, " \
               f"y: {self.pos_y})"


class LayoutProgressBar(QMainWindow):

    cur_y = 0
    last_column_size = 0
    pbs_per_column = 0
    max_pos = -1
    layout_pb = QGridLayout()

    def __init__(self, ref_app: "App",
                 input_width: int,
                 input_height: int,
                 progress_bars: dict[int, CustomProgressBar] = None):
        super().__init__()
        self.ref_app = ref_app
        self.input_width = input_width
        self.input_height = input_height
        self.progress_bars = progress_bars if progress_bars is not None else {}

        self.widget = QWidget()
        self.widget.setLayout(self.layout_pb)
        self.setCentralWidget(self.widget)

    def update_progressbar(self, track_id: int):
        self.progress_bars[track_id].setValue(
            self.progress_bars[track_id].value() + 1
        )

    def remove_progressbar(self, track_id: int):
        # remove progressbar
        progressbar_del, pb_pos_in_layout = self.get_progress_bar(track_id)
        self.cur_y -= progressbar_del.height()
        self.layout_pb.removeWidget(progressbar_del)
        progressbar_del.setParent(None)
        del self.progress_bars[track_id]
        # move every progressbar after the deleted one
        for progressbar in self.get_progress_bars(start=pb_pos_in_layout):
            self.layout_pb.removeWidget(progressbar)
            progressbar.setParent(None)
            # set new column
            if progressbar.pos_y == 0:
                progressbar.set_pos(progressbar.pos_x - 1, self.pbs_per_column)
                self.layout_pb.addWidget(progressbar,
                                         progressbar.pos_y, progressbar.pos_x)
            # set new row
            else:
                progressbar.set_pos(progressbar.pos_x, progressbar.pos_y - 1)
                self.layout_pb.addWidget(progressbar, progressbar.pos_y,
                                         progressbar.pos_x)
        # set pbs_per_column
        if self.pbs_per_column == 1:
            self.pbs_per_column = 0
            return
        max_pbs_y = 0
        for progressbar in self.progress_bars.values():
            if progressbar.pos_x == 0:
                if progressbar.pos_y > max_pbs_y:
                    max_pbs_y = progressbar.pos_y
        self.pbs_per_column = max_pbs_y + 1
        self.setFixedHeight(
            self.pbs_per_column * list(self.progress_bars.values())[0].height()
        )

    def create_progress_bar(self, track):
        self.max_pos += 1
        progress_bar = CustomProgressBar(track.id)
        progress_bar.setMaximum(8)
        progress_bar.setMinimumSize(500, 50)
        progress_bar.setMaximumSize(500, 50)
        progress_bar.setFormat(track.get_filename())
        progress_bar.setValue(1)
        self.cur_y += progress_bar.height()
        self.progress_bars[track.id] = progress_bar
        self.add_progress_bar_to_layout(progress_bar)

    def add_progress_bar_to_layout(self, progressbar: CustomProgressBar):
        self.last_column_size += progressbar.height()
        # check if no progressbar exists
        if self.layout_pb.count() == 0:
            progressbar.set_pos(0, 0)
            self.layout_pb.addWidget(progressbar, 0, 0)
            self.pbs_per_column += 1
            return

        x = self.layout_pb.itemAt(
            self.layout_pb.count() - 1
        ).widget().pos_x
        # add new column
        if self.ref_app.y() + self.input_height + self.last_column_size \
                > self.ref_app.screen().size().height():
            progressbar.set_pos(x + 1, 0)
            self.last_column_size = 0
            self.layout_pb.addWidget(progressbar, 0, x + 1)
        # add new row
        else:
            y = self.layout_pb.itemAt(
                self.layout_pb.count() - 1
            ).widget().pos_y + 1
            self.pbs_per_column += 1 if self.pbs_per_column <= y else 0
            progressbar.set_pos(x, y)
            self.layout_pb.addWidget(progressbar, y, x)

    def resize_app(self):
        if len(self.progress_bars) == 0:
            return
        progress_bar_height = list(self.progress_bars.values())[0].height()
        column = 0
        row = -1
        for i, progress_bar in enumerate(self.progress_bars.values()):
            row += 1
            if self.progress_bar_exists(progress_bar, row, column):
                continue
            if self.ref_app.y() \
                    + self.input_height \
                    + self.height() \
                    + progress_bar_height \
                    > self.ref_app.screen().size().height():
                column += 1
                row = 0
                if self.progress_bar_exists(progress_bar, row, column):
                    continue
            # self.layout_pb.itemAtPosition(row, column).widget().setParent(None)
            self.layout_pb.addWidget(progress_bar, row, column)

    def get_progress_bar(self, track_id: int) -> tuple:
        for i in range(self.layout_pb.count()):
            progressbar = self.layout_pb.itemAt(i).widget()
            if progressbar.track_id == track_id:
                return progressbar, i

    def get_progress_bars(self, start=0, step=1) -> list[CustomProgressBar]:
        progress_bars = []
        for i in range(start, self.layout_pb.count(), step):
            progress_bars.append(self.layout_pb.itemAt(i).widget())
        return progress_bars

    def p(self):
        for i in range(self.layout_pb.count()):
            print(self.layout_pb.itemAt(i).widget())

    # def progress_bar_exists(self, progress_bar, row, column):
    #     if self.layout_pb.itemAtPosition(row, column) is not None:
    #         if self.layout_pb.itemAtPosition(row, column).widget() \
    #                 == progress_bar:
    #             return True
    #     return False


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

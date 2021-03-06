import pytube
import os
import pathlib

import eyed3
from eyed3.id3.frames import ImageFrame
from urllib.request import urlretrieve


def replace_illegal_chars(path: str) -> str:
    path = path.replace("/", "")
    path = path.replace("\\", "")
    path = path.replace(":", "")
    path = path.replace("*", "")
    path = path.replace("?", "")
    path = path.replace("|", "")
    path = path.replace("\"", "")
    path = path.replace("<", "")
    return path.replace(">", "")


PATH_TEMP = "Temp"
FILE_SUFFIX_DOWNLOAD = ".spotify_download"
THUMBNAIL_SUFFIX = "-thumbnail.png"


class Downloader:
    def __init__(self,
                 video: pytube.YouTube,
                 spotify,
                 target: str,
                 pipe: "multiprocessing.connection.PipeConnection"):
        assert os.path.isdir(target)

        self.video = video
        self.spotify = spotify
        self.target = target
        self.pipe = pipe

    def download_song(self):
        self.pipe.send(self.spotify.id)
        self.video.streams.get_audio_only().download(
            PATH_TEMP,
            self.spotify.get_filename() + FILE_SUFFIX_DOWNLOAD
        )
        self.pipe.send(self.spotify.id)
        self._format_song()
        self.pipe.send(self.spotify.id)
        self._add_song_data()
        self.pipe.send(self.spotify.id)
        self._add_thumbnail()

    def _format_song(self):
        os.system(
            f"ffmpeg -loglevel quiet -i "
            f"\"{os.path.join(PATH_TEMP, self.spotify.get_filename())}"
            f"{FILE_SUFFIX_DOWNLOAD}\" "
            f"-af silenceremove=start_periods=1:start_silence=0.1:"
            f"start_threshold=-50dB,areverse,"
            f"silenceremove=start_periods=1:start_silence=0.1:"
            f"start_threshold=-50dB,areverse "
            f"\"{os.path.join(PATH_TEMP, self.spotify.get_filename())}.mp3\""
        )
        os.remove(f"{os.path.join(PATH_TEMP, self.spotify.get_filename())}"
                  f"{FILE_SUFFIX_DOWNLOAD}")

    def _add_song_data(self):
        file = eyed3.load(
            f"{os.path.join(PATH_TEMP, self.spotify.get_filename())}"
            f".mp3"
        )
        if file.tag is None:
            file.initTag()

        file.tag.artist = "; ".join(self.spotify.get_artist_names())
        file.tag.album = self.spotify.get_album_name()
        file.tag.album_artist = "; ".join(
            self.spotify.get_album_artist_names()
        )
        file.tag.title = self.spotify.get_name()
        file.tag.save()

    def _add_thumbnail(self):
        thumbnail_path = os.path.join(
            PATH_TEMP,
            replace_illegal_chars(self.spotify.get_name() + THUMBNAIL_SUFFIX)
        )

        # get thumbnail
        thumbnail_url = self.spotify.get_album_thumbnail_url()
        if thumbnail_url is None:
            thumbnail_url = self.video.thumbnail_url
        urlretrieve(thumbnail_url, thumbnail_path)

        # add thumbnail
        file = eyed3.load(
            f"{os.path.join(PATH_TEMP, self.spotify.get_filename())}"
            f".mp3"
        )
        if file.tag is None:
            file.initTag()
        file.tag.images.set(ImageFrame.FRONT_COVER,
                            open(thumbnail_path, "rb").read(),
                            "image/jpeg")
        file.tag.save()
        os.remove(thumbnail_path)

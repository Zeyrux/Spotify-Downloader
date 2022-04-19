import pytube
import os


def replace_illegal_chars(path) -> str:
    path = path.replace("/", "")
    path = path.replace("\\", "")
    path = path.replace(":", "")
    path = path.replace("*", "")
    path = path.replace("?", "")
    path = path.replace("|", "")
    path = path.replace("\"", "")
    path = path.replace("<", "")
    return path.replace(">", "")


def download_song(video: pytube.YouTube, output_path):
    assert os.path.isdir(output_path)
    video.streams.get_audio_only().download(output_path,
                                            video.title + ".spotify_download")
    os.system(f"ffmpeg -i "
              f"\"{os.path.join(output_path, video.title)}.spotify_download\" "
              f"\"{os.path.join(output_path, video.title)}.mp3\"")

    os.remove(f"{os.path.join(output_path, video.title)}.spotify_download")

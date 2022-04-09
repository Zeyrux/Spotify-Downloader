import os
import shutil
import sys
import pathlib
import datetime


BLACKLIST = ["ffmpeg.exe",
             "main.py",
             "venv",
             "git",
             ".idea",
             ".spotdl-cache"]
CUR_DIR = sys.argv[0].replace("/", "\\")
CUR_DIR = CUR_DIR[:CUR_DIR.rindex("\\")]
DOWNLOAD_DIR = os.path.expanduser("~") + "\\downloads"


def is_playlist() -> bool:
    is_playlist = False
    for path in os.listdir("./"):
        if path not in BLACKLIST:
            if is_playlist:
                return True
            is_playlist = True
    return False


def move():
    is_pl = is_playlist()
    playlist_name = datetime.datetime.today().strftime('%Y-%m-%d %H;%M;%S')
    if is_pl:
        pathlib.Path(os.path.join(DOWNLOAD_DIR, playlist_name)).mkdir(
            parents=True,
            exist_ok=True
        )
    for path in os.listdir("./"):
        if path in BLACKLIST:
            continue
        if is_pl:
            shutil.move(os.path.join(CUR_DIR, path),
                        os.path.join(DOWNLOAD_DIR, playlist_name, path))
        else:
            shutil.move(os.path.join(CUR_DIR, path),
                        os.path.join(DOWNLOAD_DIR, path))


def main():
    URL = input("URL: ")
    os.system(f"spotdl {URL}")
    print("Move to download dir")
    move()
    print("Moved")


if __name__ == '__main__':
    main()

import sys

from os import mkdir
from sys import platform
from shutil import rmtree
from pathlib import Path
from mimetypes import guess_type

from kivy.logger import Logger

if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.

    # This is path to files of exe at runtime
    application_path = sys._MEIPASS

    # This is path to exe
    # application_path = Path(sys.executable)
    Logger.info(f"Utils: Bin {application_path}")
else:
    # This is path to main.py
    application_path = Path(__file__).parent.resolve()
    Logger.info(f"Utils: Script {application_path}")


def get_tracks() -> list[str]:
    queue_length = len(sys.argv)
    if queue_length > 1:
        tracks = tracks_handler(sys.argv[1:])
    # Logger.info(f'Utils: {tracks}')
        return tracks
    return None

def is_audio(path: Path) -> bool:
    type = guess_type(path)[0]
    if type == None:
        # Logger.info(f"{path, type} is not known by mimetypes")
        return False
    if type.split(sep='/')[0] == 'audio':
        # Logger.info(f"{path} is audio")
        return True
    return False

def tracks_handler(tracks_path: list[str]) -> list[str]:
    tracks: list[str] = []
    for path in tracks_path:
        path = Path(path)
        if not(path.exists()):
            # Logger.info(f"{path} doesn't exist")
            continue
        if path.is_file():
            if is_audio(path):
                tracks.append(str(path))
                continue
        if path.is_dir():
            # Logger.info(f"{path} is directory")
            for subpath in path.glob('*'):
                tracks_path.append(str(subpath))
                continue
    tracks.sort()
    return tracks


def get_audio_provider() -> str:
    if platform == "linux":
        return "ffpyplayer"
    if platform == "win32":
        return "gstplayer"
    if platform == "darwin":
        return "ffpyplayer"
    raise ValueError(f"Utils: Cannot get audio provider for {platform}")


def get_cache_dir() -> Path:
    if platform == "linux":
        return Path.home().joinpath(".cache/smpl/")
    if platform == "win32":
        return Path.home().joinpath("AppData/Local/smpl/")
    if platform == "darwin":
        return Path.home().joinpath("Library/Caches/smpl/")
    # if platform == "android":
    #     return Path(Path.home().joinpath(".cache/smpl"))
    raise ValueError(f"Utils: Cannot get cache dir for {platform}")

def clear_cache():
    cache_dir = get_cache_dir()
    try:
        rmtree(cache_dir)
    except FileNotFoundError:
        Logger.info(f"{cache_dir} doens't exist")
    mkdir(cache_dir)

tracks = get_tracks()

import sys

from pathlib import Path
from mimetypes import guess_type

from kivy.logger import Logger

tracks = []

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.

    # This is path to files of exe at runtime
    application_path = sys._MEIPASS

    # This is path to exe
    # application_path = Path(sys.executable)
    Logger.info(f'bin {application_path}')
else:
    # This is path to main.py
    application_path = Path(__file__).parent.resolve()
    Logger.info(f'script {application_path}')

def get_tracks() -> list[str]:
    tracks = [f"{application_path}/music/[2138127990] ReyYamada (アニメの冒険の世界) - Girls' Frontline 2 Exilium - Corposant Pt2 (Main menu).m4a",
                              f"{application_path}/music/01 Vanguard Sound - One Hit Kill (游戏《少前2：追放》活动「狂想四重奏」原声音乐).m4a"]
    queue_length = len(sys.argv)
    if queue_length > 1:
        tracks = tracks_handler(sys.argv[1:])
    Logger.info(f'Utils: {tracks}')
    return tracks

def tracks_handler(tracks_path: list[str]) -> list[str]:
    def is_audio(path: Path) -> bool:
        type = guess_type(path)[0]
        if type == None:
            Logger.info(f"{path, type} is not known by mimetypes")
            return False
        if type.split(sep='/')[0] == 'audio':
            Logger.info(f"{path} is audio")
            return True
        return False

    tracks: list[str] = []
    for path in tracks_path:
        path = Path(path)
        if not(path.exists()):
            Logger.info(f"{path} doesn't exist")
            continue
        if path.is_file():
            if is_audio(path):
                tracks.append(str(path))
                continue
        if path.is_dir():
            Logger.info(f"{path} is directory")
            for subpath in path.glob('*'):
                tracks_path.append(str(subpath))
                continue
    tracks.sort()
    return tracks

tracks = get_tracks()

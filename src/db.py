from os import makedirs
from pathlib import Path
from sqlite3 import connect

from kivy.logger import Logger

from utils import get_cache_dir, is_audio
from metadata import Metadata, RawMetadata

db_path = Path(get_cache_dir()).joinpath("songs.db")

def create_db(audio_paths: list[Path|str]):
    con = connect(db_path)
    cur = con.cursor()
    cur.execute("CREATE TABLE song(album_pos, album, title, artist, length, year, image, file)")
    for audio_path in audio_paths:
        audio_path = Path(audio_path)
        for path in audio_path.rglob('*'):
            if is_audio(path):
                mt = RawMetadata(path)
                if mt.tag.track is None:
                    album_pos = 0
                else:
                    album_pos = mt.tag.track
                if mt.tag.album is None:
                    album = "Unknown album"
                else:
                    album = mt.tag.album
                if mt.tag.title is None:
                    title = "Unknown name"
                else:
                    title = mt.tag.title
                if mt.tag.albumartist is None:
                    if mt.tag.artist is None:
                        artist = "Unknown artist"
                    else:
                        artist = mt.tag.artist
                else:
                    artist = mt.tag.artist
                if mt.tag.duration is None:
                    # TODO: probably player will fail
                    length = 0
                else:
                    length = mt.tag.duration
                if mt.tag.year is None:
                    year = 0
                else:
                    year = mt.tag.year
                image = mt.image_path
                data = (album_pos, album, title, artist,
                        length, year, image, str(path))
                # insert values into a table
                # cu.execute("insert into lang values (?, ?)", ("C", 1972))
                Logger.info(f"DB: data for {path} - {data}")
                cur.execute("INSERT INTO song VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            data)
    con.commit()
    con.close()


def remove_db():
    try:
        db_path.unlink()
    except FileNotFoundError:
        Logger.error(f"DB: {db_path} doesn't exist")


def db_exists() -> bool:
    makedirs(db_path.parent, exist_ok=True)
    con = connect(db_path)
    cur = con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master")
    res = res.fetchone()
    if res is None:
        con.close()
        return False
    else:
        con.close()
        return True


def get_all_tracks() -> list[Metadata]:
    con = connect(db_path)
    cur = con.cursor()
    query = cur.execute("SELECT *, rowid FROM song ORDER BY title")
    res = query.fetchall()
    for i in range(len(res)):
        # print(res[i])
        res[i] = Metadata(res[i])
    # Logger.info(f"DB: res - {res}, type - {type(res)}")
    con.close()
    return res


class Album:
    def __init__(self, title: str, year: int, image: Path|str, artist: str, tracks_amount=0, duration=0):
        self.title: str = title
        self.year: int = year
        self.image: str = str(image)
        self.artist: str = artist

        self.tracks_amount: int = tracks_amount
        self.duration: float = duration


def get_all_albums() -> list[Album]:
    con = connect(db_path)
    cur = con.cursor()
    query = cur.execute("SELECT DISTINCT album, year, image, artist FROM song ORDER BY album")
    res = query.fetchall()
    for i, album in enumerate(res):
        res[i] = Album(album[0], album[1], album[2], album[3])
    con.close()
    return res


class Artist:
    def __init__(self, name: str, image: Path|str, album_amount: int = 0):
        self.name = name
        self.image = str(image)

        self.album_amount = album_amount


def get_all_artists() -> list[Artist]:
    con = connect(db_path)
    cur = con.cursor()
    query = cur.execute("SELECT DISTINCT artist FROM song ORDER BY artist")
    res = query.fetchall()
    for i, artist in enumerate(res):
        query = cur.execute("SELECT DISTINCT image FROM song WHERE artist = (?)", artist)
        image = query.fetchone()
        res[i] = Artist(artist[0], image[0])
    con.close()
    return res


def get_album_tracks(album: str) -> list[Metadata]:
    con = connect(db_path)
    cur = con.cursor()
    query = cur.execute("SELECT *, rowid FROM song WHERE album = (?) ORDER BY album_pos",
                        [album])
    res = query.fetchall()
    for i in range(len(res)):
        res[i] = Metadata(res[i])
    con.close()
    return res


def get_artist_albums(artist: str) -> list[Album]:
    con = connect(db_path)
    cur = con.cursor()
    query = cur.execute("SELECT DISTINCT album, year, image, artist FROM song WHERE artist = (?) ORDER BY year", (artist,))
    res = query.fetchall()
    for i, album in enumerate(res):
        res[i] = Album(album[0], album[1], album[2], album[3])
    con.close()
    return res

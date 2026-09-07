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


def get_all() -> list[Metadata]:
    con = connect(db_path)
    cur = con.cursor()
    query = cur.execute("SELECT *, rowid FROM song")
    res = query.fetchall()
    for i in range(len(res)):
        print(res[i])
        res[i] = Metadata(res[i])
    Logger.info(f"DB: res - {res}, type - {type(res)}")
    con.close()
    return res

# con = sql.connect("test.db")
# cur = con.cursor()
# try:
#     cur.execute("CREATE TABLE song(album_pos, album, title, artist, length, year, image, file)")
# except sql.OperationalError:
#     pass
# res = cur.execute("SELECT name FROM sqlite_master")
# print(f"table: {res.fetchone()}")
#
# # cur.execute("""
# #         INSERT INTO song VALUES
# #             (0, "Unknown album", "Unknown title", "Unknown artist", 69, 2069, "/home/black-fox/smpl/resources/images/no_image.jpg", ""),
# #             (1, "Unknown album1", "Unknown title1", "Unknown artist1", 169, 1969, "/home/black-fox/smpl/resources/images/no_image.jpg", "")
# # """)
# # con.commit()
#
# res = cur.execute("SELECT * FROM song")
# for i in res:
#     print(i)
# res = cur.execute("SELECT rowid, year FROM song WHERE length > 100")
# for i in res:
#     print(f"row id: {i[0]}")
#     print(f"song year: {i[1]}")
# con.close()

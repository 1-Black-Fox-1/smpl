from io import BytesIO
from pathlib import Path
from os import makedirs
from os.path import exists

# https://github.com/tinytag/tinytag
from tinytag import Image, TinyTag
from kivy.logger import Logger
from kivy.core.image import Image as CoreImage

from utils import application_path, get_cache_dir

cache_dir = get_cache_dir()

# TODO check none for tags before saving image to cache
# TODO RawMetadata can generate None.jpg
# TODO Check for multiple artists


class RawMetadata:

    def __init__(self, path_to_file: Path):
        self.tag: TinyTag = TinyTag.get(path_to_file)
        self.image_path = str(cache_dir.joinpath(f"album-cover/{self.tag.artist}/{self.tag.album}.jpg"))
        if not(exists(self.image_path)):
            self.tag: TinyTag = TinyTag.get(path_to_file, image=True)
            self._image: Image | None = self.tag.images.any
            if self._image == None:
                self.image_path = f"{application_path}/resources/images/no_image.jpg"
                Logger.info(f"Metadata: Image didn't found for {self.image_path}")
            else:
                Logger.info(f"Metadata: Getting image info {self.image_path}")
                self.image = CoreImage(BytesIO(self._image.data), ext="jpg")
                makedirs(Path(self.image_path).parent, exist_ok=True)
                Logger.info(f"Metadata: Saving {self.image_path}")
                self.image.save(self.image_path)


class Metadata:
    # def __init__(self, album_pos, album, title, artist, length, year, image, file):
    #     self.album_pos = album_pos
    #     self.album = album
    #     self.title = title
    #     self.artist = artist
    #     self.length = length
    #     self.year = year
    #     self.image = image
    #     self.file = file

    def __init__(self, metadata):
        self.album_pos = metadata[0]
        self.album = metadata[1]
        self.title = metadata[2]
        self.artist = metadata[3]
        self.length = metadata[4]
        self.year = metadata[5]
        self.image = metadata[6]
        self.file = metadata[7]
        self.id = metadata[8]

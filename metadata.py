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

#TODO check none for tags before saving image to cache
class Metadata:

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

from io import BytesIO
from shutil import rmtree
from pathlib import Path
from os import mkdir
from os.path import exists

# https://github.com/tinytag/tinytag
from sys import platform

from tinytag import Image, TinyTag
from kivy.logger import Logger
from kivy.core.image import Image as CoreImage

from utils import application_path

# TODO: move this to utils
def get_cache_dir() -> Path:
    if platform == 'linux':
        return Path.home().joinpath('.cache/smpl')
    if platform == 'win32':
        return Path.home().joinpath('AppData/Local/smpl')
    if platform == 'darwin':
        return Path.home().joinpath('Library/Caches/smpl')
    # if platform == 'android':
    #     return Path(Path.home().joinpath('.cache/smpl'))
    raise ValueError(f'Cannot get cache dir for {platform}')

# TODO: move this to utils
def create_dir(path: Path):
    try:
        mkdir(path)
        Logger.info(f'created {path}')
    except:
        Logger.info(f'{path} already exists')

cache_dir = get_cache_dir()
create_dir(cache_dir)

#TODO check none for tags before saving image to cache
class Metadata:

    def __init__(self, path_to_file: Path):
        self.tag: TinyTag = TinyTag.get(path_to_file)
        self.image_path = str(cache_dir.joinpath(f'{self.tag.artist}/{self.tag.album}.jpg'))
        if not(exists(self.image_path)):
            self.tag: TinyTag = TinyTag.get(path_to_file, image = True)
            self._image: Image | None = self.tag.images.any
            if self._image == None:
                self.image_path = f"{application_path}/resources/images/no_image.jpg"
                Logger.info(f"Metadata: Image didn't found for {self.image_path}")
            else:
                Logger.info(f'Metadata: Getting image info {self.image_path}')
                self.image = CoreImage(BytesIO(self._image.data), ext='jpg')
                create_dir(Path(cache_dir.joinpath(str(self.tag.artist))))
                Logger.info(f'Metadata: Saving {self.image_path}')
                self.image.save(self.image_path)

# def clear_cache():
#     cache_dir = './cache/'
#     try:
#         rmtree('./cache/*')
#     except FileNotFoundError:
#         Logger.info(f"{cache_dir} doens't exist")
    # mkdir('./cache/')


# TODO: make it in json? and read it from there
from utils import application_path


class Padding:
    # box: tuple[int, int] = 25, 25
    box: tuple[int, int] = 20, 10
    buttons: tuple[int, int] = 10, 10

class Spacing:
    title: int = 5
    box: int = 15
    player_buttons: int = 15

class Color:
    background: tuple[int, int, int, float] = 37, 36, 34, 0.15
    # now_playing_background = background
    now_playing_background = 37, 36, 34, 0.3
    foreground: tuple[int, int, int, float] = 255, 140, 0, 1
    slider_track = foreground

class Size:
    minimal: tuple[int, int] = 450, 700
    title_font: str = "16sp"
    # title_size: tuple[int | None, int | None] = (300, None)
    artist_font: str = "14sp"
    queue_title_font: str = "14sp"
    queue_artist_font: str = "12sp"
    queue_duration_font: str = "14sp"

    image = [1., .55]
    title = [1., .1]
    play_buttons = [1., .15]
    time = [1., .05]
    slider = [1., .03]
    top_buttons = [1., 0.05]
    queue = [1., 0.05]


class Font:
    main = f'{application_path}/resources/fonts/Noto_Sans,Noto_Sans_JP/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf'


# TODO: class image

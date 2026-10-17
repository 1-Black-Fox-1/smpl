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
    background = (0x1b/255, 0x1d/255, 0x1e/255, 1)
    # now_playing_background = background
    now_playing_background = (2 * 0x1b/255, 2 * 0x1d/255, 2 * 0x1e/255, 1)
    foreground = (0xff/255, 0xbf/255, 0x00/255, 1)
    slider_track = foreground

class Size:
    minimal: tuple[int, int] = 450, 700
    title_font: str = "16sp"
    artist_font: str = "14sp"
    queue_title_font: str = "15sp"
    queue_artist_font: str = "13sp"
    queue_duration_font: str = "15sp"
    image = [1., .72]
    title = [1., .09]
    play_buttons = [1., .08]
    time = [1., .05]
    slider = [1., .02]
    top_buttons = [1., 0.05]
    queue = [1., 0.03]


class Font:
    main = f'{application_path}/resources/fonts/Noto_Sans,Noto_Sans_JP/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf'


# TODO: class image

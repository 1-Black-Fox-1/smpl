from kivy.logger import Logger


class Padding:
    box: tuple[int, int] = 20, 10
    buttons: tuple[int, int] = 10, 10


class Spacing:
    title: int = 5
    box: int = 15
    player_buttons: int = 15


class Color:
    def __init__(self, name="VLC"):
        self.name = name
        self.background = None
        self.background_secondary = None
        self.primary = None
        self.border = None
        self.icon = None
        self.secondary = None
        self.text = None
        self.button_text = None
        self.transparent = (0, 0, 0, 0)

        match name:
            # black-white-orange theme, VLC-ish black theme
            case "VLC":
                self.primary = (0x12/255, 0x12/255, 0x12/255, 1)  # black
                self.background = self.primary
                self.background_secondary = (0x21/255, 0x21/255, 0x21/255, 1)  # grey
                self.secondary = (0xff/255, 0x95/255, 0x0d/255, 1)  # orange
                self.text = (1, 1, 1, 1)
                self.button_text = (1, 1, 1, 1)
                self.border = self.secondary
                self.icon = (1, 1, 1, 1)

            # Lilac AMOLED, black-white-purple theme from noctalia
            case "Lilac AMOLED":
                self.primary = (0x00/255, 0x00/255, 0x00/255, 1)  # pure black
                self.background = self.primary
                self.background_secondary = (0x11/255, 0x0d/255, 0x1a/255, 1)  # grey-purple
                self.border = (0x4c/255, 0x3a/255, 0x70/255, 1)
                self.secondary = (0xb5/255, 0x8f/255, 0xff/255, 1)  # bright purple
                self.text = (1, 1, 1, 1)
                self.button_text = (0xc7/255, 0x9a/255, 0xff/255, 1)  # dullest purple
                self.icon = (1, 1, 1, 1)

            case _:
                Logger.error(f"Unknown theme {self.name}")
                self.primary = (0x12/255, 0x12/255, 0x12/255, 1)  # black
                self.background = self.primary
                self.background_secondary = (0x21/255, 0x21/255, 0x21/255, 1)  # grey
                self.secondary = (0xff/255, 0x95/255, 0x0d/255, 1)  # orange
                self.text = (1, 1, 1, 1)
                self.button_text = (1, 1, 1, 1)
                self.border = self.secondary
                self.icon = (1, 1, 1, 1)


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


# TODO: class image

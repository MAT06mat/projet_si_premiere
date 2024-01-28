from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label

from custom_resize_button import CustomToggleButton
from bluetooth import BlueTooth, Api

Builder.load_file("screens/main_menu_screen.kv")


class SpeedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Api.bind(self.on_message)
        self.text = ""
    
    def on_message(self, text):
        self.text = f"Vitesse actuelle : {round(Api.speed/36, 2)}km/h"


class Arrow(CustomToggleButton):
    pass


class RightArrow(Arrow):
    def on_down(self):
        self.parent.left_arrow.up()
        BlueTooth.send("right")

    def on_up(self):
        BlueTooth.send("stop_right")


class LeftArrow(Arrow):
    def on_down(self):
        self.parent.right_arrow.up()
        BlueTooth.send("left")
    
    def on_up(self):
        BlueTooth.send("stop_left")


class MainMenuScreen(RelativeLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.speed_label = SpeedLabel()
        self.left_arrow = LeftArrow()
        self.right_arrow = RightArrow()
        self.add_widget(self.speed_label)
        self.add_widget(self.left_arrow)
        self.add_widget(self.right_arrow)
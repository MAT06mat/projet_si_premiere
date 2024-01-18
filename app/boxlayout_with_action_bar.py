from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.metrics import dp

from custom_resize_button import CustomResizeButton


class CustomResizeButton(CustomResizeButton):
    pass


Builder.load_file("boxlayout_with_action_bar.kv")


class BoxLayoutWithActionBar(BoxLayout):
    title = StringProperty()


class MyBar(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.height = dp(50)
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from bluetooth import Api

Builder.load_file("screens/velo_screen.kv")



class SpeedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Api.bind(self.on_message)
        self.text = "0"
    
    def on_message(self, text):
        self.text = str(Api.speed)


class MainMenuScreen(RelativeLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.speed_label = SpeedLabel()
        self.add_widget(self.speed_label)
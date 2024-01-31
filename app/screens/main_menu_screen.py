from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.clock import Clock

from custom_resize_button import CustomToggleButton, CustomResizeButton
from bluetooth import BlueTooth, Api

Builder.load_file("screens/main_menu_screen.kv")


class SpeedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Api.bind(self.on_message)
        self.text = ""
    
    def on_message(self, text):
        self.text = f"Acc: {Api.acc}, Var: {Api.acc - Api.last_acc}"


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


class StopButton(CustomResizeButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.loop, 1/60)
    
    def loop(self, *args):
        self.pos = (self.parent.left_arrow.x, self.parent.left_arrow.y - self.parent.left_arrow.x - self.height)
        self.width = self.parent.left_arrow.width * 2 + self.parent.left_arrow.x * 1.2
        self.height = self.width * 0.268
    
    def on_press(self):
        BlueTooth.send("stop")
        return super().on_press()
    
    def on_touch_move(self, touch):
        if self.last_press and self.collide_point(*touch.pos) and not self.touch_inside:
            BlueTooth.send("stop")
        elif self.last_press and not self.collide_point(*touch.pos) and self.touch_inside:
            BlueTooth.send("stop_stop")
        return super().on_touch_move(touch)
    
    def on_custom_press(self, *args):
        BlueTooth.send("stop_stop")
        return super().on_custom_press(*args)


class MainMenuScreen(RelativeLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.speed_label = SpeedLabel()
        self.left_arrow = LeftArrow()
        self.right_arrow = RightArrow()
        self.stop_button = StopButton()
        self.add_widget(self.speed_label)
        self.add_widget(self.left_arrow)
        self.add_widget(self.right_arrow)
        self.add_widget(self.stop_button)
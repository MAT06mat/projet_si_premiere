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
        Clock.schedule_interval(self.on_message, 1/60)
    
    def on_message(self, text):
        try:
            self.text = f" Acc: {Api.acc}, Dist: {Api.dist}"
        except:
            pass


class Arrow(CustomToggleButton):
    pass


class RightArrow(Arrow):
    def on_down(self):
        self.parent.left_arrow.up()
        BlueTooth.send("r")

    def on_up(self):
        BlueTooth.send("s_r")


class LeftArrow(Arrow):
    def on_down(self):
        self.parent.right_arrow.up()
        BlueTooth.send("l")
    
    def on_up(self):
        BlueTooth.send("s_l")


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
            BlueTooth.send("s_stop")
        return super().on_touch_move(touch)
    
    def on_custom_press(self, *args):
        BlueTooth.send("s_stop")
        return super().on_custom_press(*args)


class WarningButton(CustomToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.loop, 1/60)
    
    def loop(self, *args):
        self.pos = (self.parent.stop_button.x, self.parent.left_arrow.top + self.parent.left_arrow.x)
        self.size = self.parent.stop_button.size
    
    def on_down(self):
        BlueTooth.send("w")
        return super().on_down()
    
    def on_up(self, *args):
        BlueTooth.send("s_w")
        return super().on_up(*args)


class MainMenuScreen(RelativeLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.speed_label = SpeedLabel()
        self.left_arrow = LeftArrow()
        self.right_arrow = RightArrow()
        self.stop_button = StopButton()
        self.warning_button = WarningButton()
        self.add_widget(self.speed_label)
        self.add_widget(self.left_arrow)
        self.add_widget(self.right_arrow)
        self.add_widget(self.stop_button)
        self.add_widget(self.warning_button)
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.animation import Animation
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
    def condition(self):
        return not self.parent.slide_bar.state


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
    
    def condition(self):
        return not self.parent.slide_bar.state
    
    def on_press(self):
        if not self.parent.slide_bar.state:
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
    
    def condition(self):
        return not self.parent.slide_bar.state
    
    def on_down(self):
        BlueTooth.send("w")
        return super().on_down()
    
    def on_up(self, *args):
        BlueTooth.send("s_w")
        return super().on_up(*args)


class SettingButton(CustomResizeButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "images/setting_button.png"
        self.pos_hint = {'top': 1, 'right': 1}
        self.size_hint = (0.1, None)
    
    def condition(self):
        return not self.parent.slide_bar.state
    
    def on_custom_press(self, *args):
        self.parent.slide_bar.start()
        return super().on_custom_press(*args)


class SlideBar(RelativeLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.state = False
        self.size_hint = (0.7, 1)
        self.pos_hint = {"right": 2}
        self.anim = Animation(d=0.5, pos_hint={"right": 0.85})
        self.anim_reverse = Animation(d=0.5, pos_hint={"right": 2})
    
    def start(self):
        if self.state:
            return
        self.state = True
        self.anim.start(self)
        self.anim_reverse.stop(self)
    
    def on_touch_down(self, touch):
        if self.x > touch.x / 2:
            self.reverse()
        return super().on_touch_down(touch)
    
    def reverse(self):
        if not self.state:
            return
        self.state = False
        self.anim.stop(self)
        self.anim_reverse.start(self)
    
    def deco(self):
        self.reverse()
        Api.deconnect()


class MainMenuScreen(RelativeLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.speed_label = SpeedLabel()
        self.left_arrow = LeftArrow()
        self.right_arrow = RightArrow()
        self.stop_button = StopButton()
        self.warning_button = WarningButton()
        self.setting_button = SettingButton()
        self.slide_bar = SlideBar()
        self.add_widget(self.speed_label)
        self.add_widget(self.left_arrow)
        self.add_widget(self.right_arrow)
        self.add_widget(self.stop_button)
        self.add_widget(self.warning_button)
        self.add_widget(self.setting_button)
        self.add_widget(self.slide_bar)
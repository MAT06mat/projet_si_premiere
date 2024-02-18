from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.app import App

from custom_resize_button import CustomResizeButton
from bluetooth import BlueTooth, Api


Builder.load_file("screens/settings_screen.kv")


class ButtonTemplate(CustomResizeButton):
    def __init__(self, var, value,**kwargs):
        super().__init__(**kwargs)
        self.var = var
        self.value = value
    
    def on_custom_press(self, *args):
        BlueTooth.send(f"{self.var}:{self.value}")
        return super().on_custom_press(*args)


class BackButton(CustomResizeButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos_hint = {"top": 0.98, "x": 0.02}
        self.source = "images/back_button.png"
        self.size_hint = (0.1, None)
    
    def on_custom_press(self, *args):
        app = App.get_running_app()
        app.manager.pop()
        return super().on_custom_press(*args)


class ColorButtons(StackLayout):
    cd = ButtonTemplate(0, 0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 0.12)
        self.cd = ButtonTemplate(var="c", value="d", text="Defaut", size_hint=(1/3, 0.5))
        self.c1 = ButtonTemplate(var="c", value="y", text="Jaune", size_hint=(1/3, 0.5))
        self.c2 = ButtonTemplate(var="c", value="g", text="Vert", size_hint=(1/3, 0.5))
        self.c3 = ButtonTemplate(var="c", value="b", text="Bleu", size_hint=(1/3, 0.5))
        self.c4 = ButtonTemplate(var="c", value="v", text="Violet", size_hint=(1/3, 0.5))
        self.c5 = ButtonTemplate(var="c", value="m", text="Tous", size_hint=(1/3, 0.5))
        self.add_widget(self.cd)
        self.add_widget(self.c1)
        self.add_widget(self.c2)
        self.add_widget(self.c3)
        self.add_widget(self.c4)
        self.add_widget(self.c5)


class MotorButtons(StackLayout):
    b1 = ButtonTemplate(0, 0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 0.08)
        self.b1 = ButtonTemplate(var="m", value="g", text="Gauche", size_hint=(0.5, 1))
        self.b2 = ButtonTemplate(var="m", value="d", text="Droite", size_hint=(0.5, 1))
        self.add_widget(self.b1)
        self.add_widget(self.b2)


class MySlider(Slider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.min = 10
        self.max = 255
        self.value = 20
    
    def on_value(self, *args):
        BlueTooth.send(f"b:{self.value}")


class LumButtons(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 0.08)
        self.slider = MySlider()
        self.add_widget(self.slider)


class MyLabel(Label):
    s = 1
    
    def __init__(self, s, **kwargs):
        super().__init__(**kwargs)
        self.s = s


class BoxScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.orientation = "vertical"
        self.title_label = MyLabel(text="Réglages", size_hint=(1, 0.1), s=10, color=(0, 0, 0, 1))
        self.add_widget(self.title_label)
        self.add_widget(MyLabel(text="", size_hint=(1, 0.02), s=12))
        self.color_label = MyLabel(text="Thèmes de couleurs", size_hint=(1, 0.12), s=12, color=(0.2, 0.2, 0.2, 1))
        self.add_widget(self.color_label)
        self.color_buttons = ColorButtons()
        self.add_widget(self.color_buttons)
        self.add_widget(MyLabel(text="", size_hint=(1, 0.1), s=12))
        self.motor_label = MyLabel(text="Synchroniser le moteur", size_hint=(1, 0.12), s=12, color=(0.2, 0.2, 0.2, 1))
        self.add_widget(self.motor_label)
        self.motor_buttons = MotorButtons()
        self.add_widget(self.motor_buttons)
        self.add_widget(MyLabel(text="", size_hint=(1, 0.1), s=12))
        self.lum_label = MyLabel(text=f"", size_hint=(1, 0.12), s=12, color=(0.2, 0.2, 0.2, 1))
        self.add_widget(self.lum_label)
        self.lum_buttons = LumButtons()
        self.add_widget(self.lum_buttons)
        self.add_widget(MyLabel(text="", size_hint=(1, 0.04), s=12))
        Clock.schedule_interval(self.loop, 1/60)
    
    def loop(self, *args):
        # Update the brightness
        self.lum_label.text = f"Modifier la luminosité\nActuel : {Api.brightness}"


class SettingsScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.back_button = BackButton()
        self.add_widget(self.back_button)
        self.box_screen = BoxScreen()
        self.add_widget(self.box_screen)
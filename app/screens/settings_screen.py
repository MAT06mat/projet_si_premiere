from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.app import App

from custom_resize_button import CustomResizeButton
from bluetooth import BlueTooth


Builder.load_file("screens/settings_screen.kv")


class ButtonTemplate(CustomResizeButton):
    def __init__(self, var, value,**kwargs):
        super().__init__(**kwargs)
        self.var = var
        self.value = value
    
    def on_custom_press(self, *args):
        print("press", self.text)
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
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.size_hint = (1, 0.2)
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
    
    def reset(self):
        for b in self.children:
            b.reset()


class BoxScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.color_buttons = ColorButtons()
        self.add_widget(self.color_buttons)


class SettingsScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.back_button = BackButton()
        self.add_widget(self.back_button)
        self.box_screen = BoxScreen()
        self.add_widget(self.box_screen)
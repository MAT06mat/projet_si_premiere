from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.core.window import Window

Window.size = (320, 660)

from navigation_screen_manager import NavigationScreenManager
from bluetooth import Api


class MyScreenManager(NavigationScreenManager):
    pass


class SafeCyclingApp(App):
    manager = ObjectProperty(None)
    icon = "images/icon.png"
    
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        self.manager = MyScreenManager()
        return self.manager

    def on_stop(self):
        Api.continue_loop = False
        return super().on_stop()


if __name__ == '__main__':
    SafeCyclingApp().run()
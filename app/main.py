from kivy.app import App
from kivy.core.window import Window


class SafeCyclingApp(App):
    icon = "images/icon.png"
    
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)


if __name__ == '__main__':
    SafeCyclingApp().run()
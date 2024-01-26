from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.properties import ListProperty


class NavigationScreenManager(ScreenManager):
    screen_stack = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition(duration=0.2)
    
    def push(self, screen_name):
        if screen_name not in self.screen_stack:
            self.transition.direction = "left"
            self.screen_stack.append(self.current)
            self.current = screen_name

    def pop(self):
        if len(self.screen_stack) > 0:
            self.transition.direction = "right"
            screen_name = self.screen_stack[-1]
            self.current = screen_name
            del self.screen_stack[-1]
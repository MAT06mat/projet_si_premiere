from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window


class TransitionScreen(Screen):
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        self.app = App.get_running_app()
    
    def on_enter(self, *args):
        Clock.schedule_once(self.app.manager.suivant, self.app.manager.delay/60)
        return super().on_enter(*args)


class NavigationScreenManager(ScreenManager):
    screen_stack = ListProperty([])
    transition = ObjectProperty(FadeTransition(duration=0.2))
    
    def change_transition(self, transition_screen, screen_name) -> None:
        if transition_screen:
            self.transition = FadeTransition(duration=0.4)
            self.current = "TransitionScreen"
        else:
            self.transition = FadeTransition(duration=0)
            self.current = screen_name
    
    def push(self, screen_name, transition_screen=True, delay=0) -> None:
        self.delay = delay
        if screen_name not in self.screen_stack:
            self.screen_stack.append(self.current)
            self.change_transition(transition_screen, screen_name)
            self.next_current = screen_name

    def pop(self, transition_screen=True, delay=0, quit_level=False) -> None:
        self.delay = delay
        if len(self.screen_stack) > 0:
            screen_name = self.screen_stack[-1]
            del self.screen_stack[-1]
            self.change_transition(transition_screen, screen_name)
            self.next_current = screen_name
    
    def suivant(self, *arg) -> None:
        if self.next_current:
            self.current = self.next_current
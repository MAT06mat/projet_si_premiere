from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Line, Color
from kivy.clock import Clock


from custom_resize_button import CustomResizeButton


Builder.load_file("connection_screen.kv")


class AnimateImage(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.anim = Animation(d=0.5, opacity=0)
        self.anim += Animation(d=0.5, opacity=1)
        self.anim += Animation(d=2, opacity=1)
        if self.pos_hint == {"top": 1}:
            self.anim += Animation(d=2, pos_hint={"top": 2}, t='in_cubic') & Animation(d=3, opacity=0)
        else:
            self.anim += Animation(d=2, pos_hint={"y": -1}, t='in_cubic') & Animation(d=3, opacity=0)
        self.anim.start(self)


class ConnectMessage(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.pos_hint = {"top": 1, "center_x": 0.5}
        self.anim = Animation(d=1, pos_hint={"top": 0.96, "center_x": 0.5}, t='in_out_cubic')
        self.anim_2 = Animation(d=0.5, opacity=0) + Animation(d=0.5, opacity=1, t='in_out_cubic')
        self.anim_reverse = Animation(d=1, pos_hint={"top": 1, "center_x": 0.5}, t='in_out_cubic') & Animation(d=0.5, opacity=0, t='in_out_cubic')
        self.last_event = Clock.schedule_once(self.stopped_message, 10.0)
        self.last_event.cancel()

    def message(self, text):
        self.text = text
        self.anim.start(self)
        self.anim_2.start(self)
        self.last_event.cancel()
        self.last_event = Clock.schedule_once(self.stopped_message, 5.0)
    
    def stopped_message(self, *args):
        self.anim_reverse.start(self)


class ConnectLabel(Label):
    custom_test = """Bienvenue sur Safe Cycling[/size][/b][/color]\n\n
[color=6c6c6c]Pour continuer vous devez vous connecter à un appareil allumé.\n
Vérifiez que votre bluetooth est bien activé et que le périphérique est bien appairé.[/color]"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.4)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.65}
        self.valign = "center"
        self.halign = "center"
        self.markup = True
        self.opacity = 0
        self.anim = Animation(d=5, opacity=0)
        self.anim += Animation(d=1, opacity=1, t='in_out_cubic')
        self.anim.start(self)


class ConnectButton(CustomResizeButton):
    loading = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "images/connect_button.png"
        self.size_hint = (0.5, None)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.3}
        self.opacity = 0
        self.animation = Animation(d=5, opacity=0)
        self.animation += Animation(d=1, opacity=1, t='in_out_cubic')
        self.animation.start(self)
        self.animations_click_self = Animation(d=1, pos_hint={"center_x": 0.5, "center_y": 0.36}, t='in_out_cubic')
        self.animations_click_loading = Animation(d=1, pos_hint={"center_x": 0.5, "center_y": 0.24}, t='in_out_cubic')
        self.animations_click_loading &= Animation(d=1.5, opacity=1, t='in_out_cubic')
        self.animations_click_reverse_self = Animation(d=1, pos_hint={"center_x": 0.5, "center_y": 0.3}, t='in_out_cubic')
        self.animations_click_reverse_loading = Animation(d=0.5, pos_hint={"center_x": 0.5, "center_y": 0.3}, t='in_out_cubic')
        self.animations_click_reverse_loading &= Animation(d=0.5, opacity=0, t='in_out_cubic')
        self.last_event = Clock.schedule_once(self.stopped_loading, 10.0)
        self.last_event.cancel()
    
    def on_custom_press(self, *args):
        if not self.loading:
            self.animations_click_self.start(self)
            self.animations_click_loading.start(self.parent.loading)
        self.loading = True
        self.last_event.cancel()
        self.last_event = Clock.schedule_once(self.stopped_loading, 20.0)
    
    def stopped_loading(self, *args):
        self.animations_click_reverse_self.start(self)
        self.animations_click_reverse_loading.start(self.parent.loading)
        Clock.schedule_once(self.send_error_message, 0.5)
        self.loading = False
    
    def send_error_message(self, *args):
        self.parent.connect_message.message("Aucun appareil n'a été détecté")


class Loading(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.size_hint = (0.15, None)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.3}
        self.angle_void = 0
        self.anim = Animation(d=3, angle_void=360, t='in_out_sine') + Animation(d=3, angle_void=0, t='in_out_sine')
        self.anim.repeat = True
        self.anim.start(self)
        self.angle_turn = 0
        self.anim_2 = Animation(d=1.4, angle_turn=360) + Animation(d=-1.4, angle_turn=0)
        self.anim_2.repeat = True
        self.anim_2.start(self)
        Clock.schedule_interval(self.loop, 1/60)
    
    def loop(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(rgb=(0, 0.5, 1))
            Line(circle=(self.center_x, self.center_y, self.width/2, self.angle_turn, self.angle_turn + self.angle_void), width=self.width*0.04)


class Background(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.size_hint = (1, 1)
        self.anim = Animation(d=4, opacity=0)
        self.anim += Animation(d=1, opacity=1, t='in_out_cubic')
        self.anim.start(self)


class ConnectionScreen(RelativeLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background = Background()
        self.animate_image_top = AnimateImage(source="images/background_top.png", pos_hint={"top": 1})
        self.animate_image_bottom = AnimateImage(source="images/background_bottom.png", pos_hint={"y": 0})
        self.connect_message = ConnectMessage()
        self.connect_button = ConnectButton()
        self.connect_label = ConnectLabel()
        self.loading = Loading()
        self.add_widget(self.background)
        self.add_widget(self.animate_image_top)
        self.add_widget(self.animate_image_bottom)
        self.add_widget(self.connect_message)
        self.add_widget(self.connect_button)
        self.add_widget(self.connect_label)
        self.add_widget(self.loading)
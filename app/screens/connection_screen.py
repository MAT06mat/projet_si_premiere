from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Line, Color
from kivy.clock import Clock, mainthread
from kivy.app import App


from custom_resize_button import CustomResizeButton
from bluetooth import BlueTooth

import threading, asyncio, sys

if sys.platform != "win32":
    from android.permissions import request_permissions, check_permission, Permission
    # Exemple:
    # request_permissions([Permission.BLUETOOTH_CONNECT])
    # check_permission(Permission.BLUETOOTH_CONNECT)


Builder.load_file("screens/connection_screen.kv")


class AnimateImage(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.anim = Animation(d=0.5, opacity=1)
        self.anim += Animation(d=1, opacity=1)
        if self.pos_hint == {"top": 1}:
            self.anim += Animation(d=2, pos_hint={"top": 2}, t='in_cubic') & Animation(d=2, opacity=0)
        else:
            self.anim += Animation(d=2, pos_hint={"y": -1}, t='in_cubic') & Animation(d=2, opacity=0)
        self.anim.start(self)


class ConnectMessage(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.pos_hint = {"top": 1.1, "center_x": 0.5}
        self.anim = Animation(d=1, pos_hint={"top": 0.98, "center_x": 0.5}, t='in_out_cubic')
        self.anim_2 = Animation(d=0.5, opacity=0) + Animation(d=0.5, opacity=1, t='in_out_cubic')
        self.anim_reverse = Animation(d=1, pos_hint={"top": 1.1, "center_x": 0.5}, t='in_out_cubic') & Animation(d=0.5, opacity=0, t='in_out_cubic')
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.valign = "center"
        self.halign = "center"
        self.markup = True
        self.opacity = 0
        self.anim = Animation(d=2.5, opacity=0)


class ConnectTitle(ConnectLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos_hint = {"center_x": 0.5}
        self.size_hint = (0.8, 0.1)
        self.text = "[color=010101][b]Bienvenue sur Safe Cycling[/b][/color]"
        self.anim += Animation(d=1, opacity=1, t='in_out_cubic')
        self.anim.start(self)


class ConnectDescription(ConnectLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, None)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.6}
        self.text = """[color=202020]Pour continuer vous devez vous connecter à un appareil allumé.\n
Vérifiez que votre bluetooth est bien activé.[/color]"""
        self.anim += Animation(d=1, opacity=1, t='in_out_cubic') & Animation(d=1, pos_hint={"center_x": 0.5, "center_y": 0.65}, t="out_circ")
        self.anim.start(self)


class ConnectButton(CustomResizeButton):
    loading = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "images/connect_button.png"
        self.size_hint = (0.5, None)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.2}
        self.opacity = 0
        self.animation = Animation(d=2.5, opacity=0)
        self.animation += Animation(d=1, opacity=1, t='in_out_cubic') & Animation(d=1, pos_hint={"center_x": 0.5, "center_y": 0.25}, t="out_circ")
        self.animation.start(self)
        self.animations_click_self = Animation(d=0.5, pos_hint={"center_x": 0.5, "center_y": 0.32}, t='in_out_cubic')
        self.animations_click_loading = Animation(d=0.5, pos_hint={"center_x": 0.5, "center_y": 0.18}, t='in_out_cubic')
        self.animations_click_loading &= Animation(d=1, opacity=1, t='in_out_cubic')
        self.animations_click_reverse_self = Animation(d=1, pos_hint={"center_x": 0.5, "center_y": 0.25}, t='in_out_cubic')
        self.animations_click_reverse_loading = Animation(d=0.5, pos_hint={"center_x": 0.5, "center_y": 0.25}, t='in_out_cubic')
        self.animations_click_reverse_loading &= Animation(d=0.5, opacity=0, t='in_out_cubic')
    
    def condition(self):
        if sys.platform != "win32":
            if not check_permission(Permission.BLUETOOTH_CONNECT):
                request_permissions([Permission.BLUETOOTH_CONNECT])
        return not self.loading
    
    def on_custom_press(self, *args):
        if not BlueTooth.is_connect:
            if not self.loading:
                self.animations_click_self.start(self)
                self.animations_click_loading.start(self.parent.loading)
                threading.Thread(target=self.connect_bluetooth).start()
            self.loading = True
    
    def connect_bluetooth(self, *args):
        try:
            asyncio.run(BlueTooth.connect())
            self.change_screen()
        except Exception as e:
            print(f"Error connecting Bluetooth: {e}")
            error = "Aucun appareil n'est détecté"
            if sys.platform != "win32":
                if not check_permission(Permission.BLUETOOTH_CONNECT):
                    error = "L'autorisation BLUETOOTH est requise"
            self.parent.connect_message.message(error)
        finally:
            Clock.schedule_once(self.reverse_anim, 0.5)
    
    @mainthread
    def change_screen(self, *args):
        app = App.get_running_app()
        app.manager.push('MainMenu')
        
    
    def reverse_anim(self, *args):
        self.animations_click_reverse_self.start(self)
        self.animations_click_reverse_loading.start(self.parent.loading)
        self.loading = False


class Loading(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.size_hint = (0.15, None)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.25}
        self.angle_void = 10
        self.anim = Animation(d=3, angle_void=350, t='in_out_sine') + Animation(d=3, angle_void=10, t='in_out_sine')
        self.anim.repeat = True
        self.anim.start(self)
        self.angle_turn = 0
        self.anim_2 = Animation(d=1, angle_turn=360) + Animation(d=-1, angle_turn=0)
        self.anim_2.repeat = True
        self.anim_2.start(self)
        Clock.schedule_interval(self.loop, 1/60)
    
    def loop(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(rgb=(0, 0.5, 1))
            Line(circle=(self.center_x, self.center_y, self.width/2, self.angle_turn, self.angle_turn + self.angle_void), width=self.width*0.04)


class SettingButton(CustomResizeButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "images/setting_button.png"
        self.pos_hint = {'top': 0.95, 'right': 1}
        self.size_hint = (0.1, None)
        self.opacity = 0
        self.animation = Animation(d=2.5, opacity=0)
        self.animation += Animation(d=1, opacity=1, t='in_out_cubic') & Animation(d=1, pos_hint={'top': 1, 'right': 1}, t="out_circ")
        self.animation.start(self)
    
    def on_custom_press(self, *args):
        return super().on_custom_press(*args)


class Background(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.size_hint = (1, 1)
        self.anim = Animation(d=1.5, opacity=0)
        self.anim += Animation(d=1, opacity=1, t='in_out_cubic')
        self.anim.start(self)


class ConnectionScreen(RelativeLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        # self.background = Background()
        self.animate_image_top = AnimateImage(source="images/background_top.png", pos_hint={"top": 1})
        self.animate_image_bottom = AnimateImage(source="images/background_bottom.png", pos_hint={"y": 0})
        self.connect_message = ConnectMessage()
        self.setting_button = SettingButton()
        self.connect_button = ConnectButton()
        self.connect_title = ConnectTitle()
        self.connect_description = ConnectDescription()
        self.loading = Loading()
        # self.add_widget(self.background)
        self.add_widget(self.animate_image_top)
        self.add_widget(self.animate_image_bottom)
        self.add_widget(self.connect_message)
        self.add_widget(self.setting_button)
        self.add_widget(self.connect_button)
        self.add_widget(self.connect_title)
        self.add_widget(self.connect_description)
        self.add_widget(self.loading)
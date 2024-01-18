from kivy.uix.button import Button
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.image import Image
from kivy.animation import Animation


class CustomPressButton(Button):
    last_press = False
    """`Private var`"""
    
    custom_press = NumericProperty(0)
    '''Event callback property / Property for call `on_custom_press` func.

    :attr:`custom_press` is an :class:`~kivy.properties.NumericProperty` and is
    read-only.
    '''
    
    wait_end = BooleanProperty(False)
    '''Indicate if you want wait the end of the animation for call :func:`on_custom_press` func (mouse is disabled on this time).

    :attr:`wait_end` is a :class:`~kivy.properties.BooleanProperty` and defaults
    to False.
    '''
    
    def on_press(self):
        if not self.condition():
            return super().on_press()

        self.last_press = True
        return super().on_press()
    
    def on_touch_up(self, touch):
        if self.last_press and self.collide_point(*touch.pos):
            
            def callback(*args):
                App.get_running_app().click_disabled = False
                self.custom_press += 1
            
            if self.wait_end:
                # Wait the end of the animation
                Clock.schedule_once(callback, 0.11)
                App.get_running_app().click_disabled = True
            else:
                callback()
        
        self.last_press = False
        return super().on_touch_up(touch)
    
    def condition(self):
        """Condition for start animation on the `on_press` event and call `on_custom_press` func.
        `Default: return True`"""
        return True
    
    def on_custom_press(self, *args):
        """Custom press event, call after unclick the button"""


class CustomResizeButton(CustomPressButton):
    touch_inside = False
    """`Private var`"""
    
    last_press = False
    """`Private var`"""
    
    coef_size = NumericProperty(0)
    """`Private var`"""
    
    source = StringProperty('')
    '''Filename / source of your enabled button.

    :attr:`source` is a :class:`~kivy.properties.StringProperty` and
    defaults to None.
    '''
    
    disabled_source = StringProperty('')
    '''Filename / source of your disabled button.

    :attr:`disabled_source` is a :class:`~kivy.properties.StringProperty` and
    defaults to None.
    '''
    
    custom_press = NumericProperty(0)
    '''Event callback property / Property for call `on_custom_press` func.

    :attr:`custom_press` is an :class:`~kivy.properties.NumericProperty` and is
    read-only.
    '''
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (1, 1, 1, 0)
        self.image = Image(source=self.source, size=self.size, pos=self.pos)
        self.add_widget(self.image, canvas="before")
        self.bind(source=self._source_change, disabled_source=self._source_change, disabled=self._source_change)
        self.bind(size=self._update_image, coef_size=self._update_image, center=self._update_image)
        self.anim = Animation(d=0.1, t="in_out_quad", coef_size=0)
        self.anim_reverse = Animation(d=0.1, t="in_out_quad", coef_size=0.1)
    
    def _source_change(self, *args):
        if self.disabled:
            self.image.source = self.disabled_source
        else:
            self.image.source = self.source
    
    def _update_image(self, *args):
        self.image.size = (self.size[0]*(1-self.coef_size), self.size[1]*(1-self.coef_size))
        self.image.center = self.center
    
    def on_press(self):
        if not self.condition():
            return super().on_press()
        self.last_press = True
        self.touch_inside = True
        self.anim.cancel(self)
        self.anim_reverse.start(self)
        return super().on_press()
    
    def on_touch_move(self, touch):
        if self.last_press and self.collide_point(*touch.pos) and not self.touch_inside:
            self.touch_inside = True
            self.anim.cancel(self)
            self.anim_reverse.start(self)
        elif self.last_press and not self.collide_point(*touch.pos) and self.touch_inside:
            self.touch_inside = False
            self.anim.start(self)
            self.anim_reverse.cancel(self)
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self.last_press:
            self.anim.start(self)
            self.anim_reverse.cancel(self)
        return super().on_touch_up(touch)
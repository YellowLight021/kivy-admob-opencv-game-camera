# floor.py
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock  # 用于定时更新动画
from kivy.core.window import Window
from config import DOOR_SIZE_FACTOR
class Door(Image):
    def __init__(self,pos, **kwargs):
        super(Door, self).__init__(**kwargs)
        self.device_window_width, self.device_window_height = Window.size
        self.size_hint = (None, None)
        self.size = (
        DOOR_SIZE_FACTOR[0] * self.device_window_width, DOOR_SIZE_FACTOR[1] * self.device_window_height)
        self.allow_stretch = True
        self.pos = pos
        self.animations = [f"resources/door/door_frame_{i}.png" for i in range(0, 4)]
        self.frame_index = 0
        Clock.schedule_interval(self.update_animation, 0.1)  # 每 0.1 秒更新一帧
        self.opacity = 0.7
        self.source = self.animations[self.frame_index]  # 初始图像资源
    def update_animation(self,dt):
        self.frame_index = (self.frame_index + 1) % 4
        self.source = self.animations[self.frame_index]  # 更新图像资源

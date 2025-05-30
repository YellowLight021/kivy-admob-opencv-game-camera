from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock  # 用于定时更新动画
from kivy.core.window import Window
import os

def create_coin(name,**kwargs):
    # 创建一个名字到类的映射字典
    coin_classes = {
        "coin": Coin,
        "arrow_coin": ArrowCoin,
    }

    # 通过名字从字典中查找类，并实例化
    coin_class = coin_classes.get(name.lower())  # 使用 lower() 忽略大小写
    if coin_class:
        return coin_class(**kwargs)  # 实例化
    else:
        raise ValueError(f"Monster '{name}' does not exist.")
class Coin(Image):
    def __init__(self, pos, name="coin", **kwargs):
        super(Coin, self).__init__(**kwargs)
        self.device_window_width, self.device_window_height = Window.size
        self.add_value=1
        self.pos=pos
        self.size_hint = (None, None)
        self.size = (0.06875 * self.device_window_width, 0.05 * self.device_window_height)
        self.touched = False
        self.frame_index = 0  # 当前动画帧的索引
        resource_path = f"resources/money/{name}"
        self.img_num = len(os.listdir(resource_path))
        self.animations = [f"resources/money/{name}/{name}_{i}.png" for i in range(1, self.img_num + 1)]
        self.source = self.animations[self.frame_index]  # 初始图像资源
        Clock.schedule_interval(self.update_animation, 0.1)  # 每 0.1 秒更新一帧
    def update_animation(self, dt):
        self.frame_index = (self.frame_index + 1) % self.img_num
        self.source = self.animations[self.frame_index]  # 更新图像资源

class ArrowCoin(Coin):
    def __init__(self, pos, name="arrow", **kwargs):
        super(ArrowCoin, self).__init__( pos, name,**kwargs)
        self.size = (0.2 * self.device_window_width, 0.2 * self.device_window_height)
        self.add_value = 0

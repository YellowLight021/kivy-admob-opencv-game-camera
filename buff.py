# floor.py
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
import random
from kivy.core.window import Window
from kivy.clock import Clock  # 用于定时更新动画

def get_buff_type(name):
    buff_classes = {
        "health_buff": 1,
        "shield_buff": 2,
        "spiculate_buff": 3,
        "push_buff":3
    }
    return buff_classes[name]
def create_buff(name,**kwargs):
    # 创建一个名字到类的映射字典
    buff_classes = {
        "health_buff": HealthBuff,
        "shield_buff": ShieldBuff,
        "spiculate_buff": SpiculateBuff,
        "push_buff":PushBuff
    }

    if "random" in name:
        # 获取字典的值列表
        values = list(buff_classes.values())
        buff_class = random.choices(values,weights=[3,1,1,1],k=1)[0]
    else:
        # 通过名字从字典中查找类，并实例化
        buff_class = buff_classes.get(name.lower())  # 使用 lower() 忽略大小写
    if buff_class:
        return buff_class(**kwargs)  # 实例化
    else:
        raise ValueError(f"buff '{name}' does not exist.")
class Buff(Image):
    def __init__(self,pos,name="buff", **kwargs):
        super(Buff, self).__init__(**kwargs)
        self.device_window_width, self.device_window_height = Window.size
        self.size_hint=(None,None)
        self.size = (0.07* self.device_window_width, 0.06* self.device_window_height)
        self.pos = pos
        self.touched = False
        self.name = name  # 初始图像资源
        self.times=0 #持续时长
        self.buff_type=get_buff_type(name)
        self.source=f"resources/buff/{name}.png"
        print(f"buff name:{name}")




class HealthBuff(Buff):
    def __init__(self,pos,name="health_buff", **kwargs):
        super(HealthBuff, self).__init__(pos,name,**kwargs)
        self.times=1

class ShieldBuff(Buff):
    def __init__(self,pos,name="shield_buff", **kwargs):
        super(ShieldBuff, self).__init__(pos,name,**kwargs)
        self.times=600

class SpiculateBuff(Buff):
    def __init__(self,pos,name="spiculate_buff", **kwargs):
        super(SpiculateBuff, self).__init__(pos,name,**kwargs)
        self.times=600


class PushBuff(Buff):
    def __init__(self,pos,name="push_buff", **kwargs):
        super(PushBuff, self).__init__(pos,name,**kwargs)
        self.times=800

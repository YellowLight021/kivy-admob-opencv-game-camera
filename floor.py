# floor.py
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
from config import CHARACTER_SIZE_FACTOR
from kivy.core.window import Window

def create_floor(name,**kwargs):
    # 创建一个名字到类的映射字典
    floor_classes = {
        "ground_empty": EmptyFloor,
        "ground_grass": GrassFloor,
        "ground": Floor,
        "ground_spine": SpineFloor,
        "ground_dead":DeadFloor,
        "ground_move":MoveFloor
    }

    # 通过名字从字典中查找类，并实例化
    floor_class = floor_classes.get(name.lower())  # 使用 lower() 忽略大小写
    if floor_class:
        return floor_class(name,**kwargs)  # 实例化
    else:
        raise ValueError(f"Floor '{name}' does not exist.")
class Floor(Widget):
    def __init__(self,floor_name, pos, size,damage=0,speed_up=0, **kwargs):
        super(Floor, self).__init__(**kwargs)
        self.device_window_width, self.device_window_height = Window.size
        self.size_hint = (None, None)
        self.pos = pos
        self.size = size
        self.damage=damage
        #一定造成伤害无视护盾
        self.must_damage=False
        self.speed_up=speed_up
        self.allow_stretch = True
        self.keep_ratio=False
        self.name=floor_name

        self.inner_height = max(0.6 * self.size[1],
                                self.size[1] - 0.4 * self.device_window_height * CHARACTER_SIZE_FACTOR[1])
        # self.inner_height=max(0.75*self.size[1],self.size[1]-0.2*self.device_window_height*CHARACTER_SIZE_FACTOR[1])
        self.inner_rect=(self.pos[0],self.pos[1]+0.5*(self.size[1]-self.inner_height),
                         self.size[0],self.inner_height)
        # print("floor_name :{}".format(floor_name))
        with self.canvas:

            self.floor_texture = CoreImage(f"resources/floor/{floor_name}.png").texture
            # self.floor_texture = CoreImage(f"resources/floor/ground_spine.png").texture
            # self.floor_texture.wrap = 'repeat'
            Color(1, 1, 1, 1)
            self.rect =Rectangle(texture=self.floor_texture, pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics_pos)

    def update_graphics_pos(self, *args):
        self.rect.pos = self.pos
        self.inner_rect = (self.pos[0], self.pos[1] + 0.5 * (self.size[1] - self.inner_height),
                           self.size[0], self.inner_height)
    def update(self):
        pass

class EmptyFloor(Floor):
    def __init__(self,floor_name, pos, size,damage=0, **kwargs):
        super(EmptyFloor, self).__init__(floor_name, pos, size,damage,**kwargs)

class GrassFloor(Floor):
    def __init__(self,floor_name, pos, size,damage=0, **kwargs):
        super(GrassFloor, self).__init__(floor_name, pos, size,damage,**kwargs)

class SpineFloor(Floor):
    def __init__(self,floor_name, pos, size,damage=100, **kwargs):
        super(SpineFloor, self).__init__(floor_name, pos, size,damage,**kwargs)

class DeadFloor(Floor):
    def __init__(self,floor_name, pos, size,damage=9999, **kwargs):
        super(DeadFloor, self).__init__(floor_name, pos, size,damage,**kwargs)
        self.must_damage=True

class MoveFloor(Floor):
    def __init__(self,floor_name, pos, size,damage=0, **kwargs):
        super(MoveFloor, self).__init__(floor_name, pos, size,damage,**kwargs)
        #后期扩展可以专门设计特定运动的floor，在继承这个类设置初始速度调用set_velocity方法即可。这个第一次写用来给特殊关卡用的
        self.velocity_y = 0
        self.velocity_x = 0
    def set_velocity(self,v):
        self.velocity_y = v[1]
        self.velocity_x = v[0]
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        # print("floor pos:{}".format(self.pos))


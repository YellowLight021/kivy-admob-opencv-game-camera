from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
import random
from kivy.clock import Clock  # 用于定时更新动画
class Status(Image):
    # 用于显示buff状态表现的
    def __init__(self, owner,name,**kwargs):
        super(Status, self).__init__(**kwargs)
        self.owner=owner
        self.name = name
        self.update_status()

    def update(self):
        self.update_status()

    def update_status(self, *args):

        # 位置和宽度
        self.pos = self.owner.pos
        self.size=self.owner.size

class ShieldStatus(Status):
    def __init__(self,owner,name, **kwargs):
        super(ShieldStatus, self).__init__(owner,name,**kwargs)
        self.source = f"resources/status/{name}.png"
        print("buff name :{}".format(name))
        # self.opacity=0.5
    def update_status(self, *args):

        # 位置和宽度
        self.pos = (self.owner.x- self.owner.width*0.3, self.owner.y - self.owner.height*0.5)
        self.size=(self.owner.width*2,self.owner.height*2)
from kivy.uix.image import Image
from bullet import Bullet
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from kivy.properties import NumericProperty

class HealthBar(Widget):
    # 直接定义血条高度相对于怪物的比例
    relative_height = NumericProperty(0.1)  # 相对于怪物高度的 10%

    def __init__(self, monster, health=100, max_health=100, **kwargs):
        super(HealthBar, self).__init__(**kwargs)
        self.monster = monster
        self.health = health
        self.max_health = max_health

        # 更新血条的绘制
        self.bind(pos=self.update_health_bar, size=self.update_health_bar)
        self.update_health_bar()

    def update(self, health):
        """更新健康值并重新绘制血条"""
        self.health = health
        self.update_health_bar()

    def update_health_bar(self, *args):
        """根据健康值和怪物大小更新血条位置和尺寸"""
        health_ratio = self.health / self.max_health

        # 设置血条位置和宽度
        self.pos = (self.monster.x, self.monster.top + self.monster.height*self.relative_height)  # 在怪物上方 5 像素
        self.size = (self.monster.width * health_ratio, self.monster.height * self.relative_height)

        # 清空画布并重新绘制
        self.canvas.clear()
        with self.canvas:
            # 绘制黑色描边框
            Color(1, 1, 1, 0.5)  # 黑色
            border_padding = 1  # 描边的宽度，可以根据需要调整
            Rectangle(pos=(self.pos[0] - border_padding, self.pos[1] - border_padding),
                      size=(self.size[0] + 2 * border_padding, self.size[1] + 2 * border_padding))

            # 绘制血条（红色）
            Color(1, 0, 0, 1)  # 红色
            Rectangle(pos=self.pos, size=self.size)
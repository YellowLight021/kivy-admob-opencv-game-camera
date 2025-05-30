from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.core.window import Window

# MovingImage类：负责显示图片并进行动画
class MovingImage(Image):
    def __init__(self, pos_factor, size_factor=[0.12, 0.06], swing_distance_factor=0.05,if_mirror=False, **kwargs):
        super().__init__(**kwargs)
        self.source = "resources/guide/mirror_finger.png" if if_mirror else "resources/guide/finger.png"  # 设置图片路径
        self.pos_factor = pos_factor
        self.size_factor = size_factor
        self.swing_distance_factor = swing_distance_factor
        self.keep_ratio = False
        self.allow_stretch = True
        self.size_hint = (None, None)
        self.anim = None

    def animate_image(self, original_pos, swing_distance):
        # 动画范围：左右摆动
        self.anim = Animation(pos=(original_pos[0] + swing_distance, original_pos[1]), duration=0.5, t='in_out_sine') + \
                    Animation(pos=(original_pos[0] - swing_distance, original_pos[1]), duration=0.5, t='in_out_sine') + \
                    Animation(pos=original_pos, duration=0.5, t='in_out_sine')

        self.anim.repeat = True
        self.anim.start(self)

    def start_animation(self, instance=None):
        screen_width, screen_height = Window.size
        self.pos = [int(self.pos_factor[0] * screen_width), int(self.pos_factor[1] * screen_height)]
        self.size = [int(self.size_factor[0] * screen_width), int(self.size_factor[1] * screen_height)]
        swing_distance = self.swing_distance_factor * screen_width
        self.animate_image(self.pos, swing_distance)

    def stop_animation(self):
        """停止动画并释放资源"""
        if self.anim:
            self.anim.stop(self)  # 停止当前动画
            self.anim = None  # 清除动画对象

        # 如果需要移除控件，使用parent.remove_widget(self)而不是clear_widgets
        parent = self.parent
        if parent:
            parent.remove_widget(self)  # 从父控件中移除当前控件

        # 清除图像资源
        self.source = ""  # 释放图像资源
        self.canvas.clear()  # 清除绘制的内容
        print("Animation stopped and resources cleared.")

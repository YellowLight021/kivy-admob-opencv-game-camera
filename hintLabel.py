from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.utils import platform
from kivy.app import App
import os
class HintLabel(Label):
    def __init__(self, message, duration=3,color=(1, 0, 0, 1),size=(300, 50), **kwargs):
        super(HintLabel, self).__init__(
            text=message,
            size_hint=(None, None),
            size=size,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            color=color,  # 红色文字
            **kwargs
        )
        self.duration = duration


    def show(self, parent):
        """显示提示信息并自动移除"""
        parent.add_widget(self)
        Clock.schedule_once(lambda dt: parent.remove_widget(self), self.duration)



class HintImage(Image):
    def __init__(self, image_source, duration=3,size=(300,300), **kwargs):
        super(HintImage, self).__init__(
            source=image_source,
            size_hint=(None, None),
            size=size,  # 可以根据实际需要调整尺寸
            pos_hint={"center_x": 0.5, "center_y": 0.85},
            **kwargs
        )
        self.duration = duration
        self.color = (1, 1, 1, 0.75)
        self.allow_stretch = True
    def show(self, parent):
        """显示提示图片并自动移除"""
        parent.add_widget(self)
        Clock.schedule_once(lambda dt: parent.remove_widget(self), self.duration)

class HintAnimateImage(Image):
    def __init__(self, image_source, fps=1,size=(300,300),if_once=False, **kwargs):
        super(HintAnimateImage, self).__init__(
            size_hint=(None, None),
            size=size,  # 可以根据实际需要调整尺寸
            pos_hint={"center_x": 0.5, "center_y": 0.8},
            **kwargs
        )
        self.resource_path = image_source
        self.frame_names=os.listdir(self.resource_path)
        self.frame_index=0
        self.source=os.path.join(self.resource_path,self.frame_names[self.frame_index])

        self.fps = fps
        self.color = (1, 1, 1, 1)
        self.allow_stretch = True
        self.if_once=if_once

    def start_animation(self):
        if not self.if_once:
            Clock.schedule_interval(self.update_animation, self.fps)  # 每 0.1 秒更新一帧
        else:
            Clock.schedule_once(self.update_animation,self.fps)

    def update_animation(self, dt):
        self.frame_index = (self.frame_index + 1) % len(self.frame_names)
        self.source = os.path.join(self.resource_path, self.frame_names[self.frame_index])
        # print("self.frame_index:{}".format(self.frame_index))
    def show(self, parent):
        """显示提示图片并自动移除"""
        parent.add_widget(self)
        self.start_animation()

class PausePopup(ModalView):
    def __init__(self, image_source, text="continue ?",size=(400, 400), callback_0=None,callback_1=None,callback_2=None, **kwargs):
        super().__init__(**kwargs)
        self.device_window_width, self.device_window_height = Window.size
        # 设置 ModalView 背景为透明
        self.background_color = (0, 0, 0, 0)
        self.size = (self.device_window_width*0.85, self.device_window_height*0.5)  # 设置弹窗的宽高
        self.callback_0 = callback_0
        self.callback_1=callback_1
        self.callback_2 = callback_2

        bg_image_source = r"resources/background/record.png"
        # 创建一个 Image 组件加载自定义美术素材作为背景
        bg_image = Image(source=bg_image_source, size_hint=(1, 1), pos_hint={'x': 0, 'y': 0}, allow_stretch=True)
        layout = FloatLayout()
        layout.add_widget(bg_image)

        info_image = Image(source=image_source, size_hint=(0.6, 0.3), pos_hint={'center_x': 0.5, 'y': 0.4},
                           allow_stretch=True)

        message_label = Label(text=text, color=(1, 1, 1, 1), size_hint=(0.3, 0.05),
                              pos_hint={'center_x': 0.5, 'y': 0.3})

        button_0 = Button(background_normal= "resources/button/start_game.png",
                          background_down="resources/button/start_game.png",
                          border=(0, 0, 0, 0),
                          size_hint=(0.3, 0.15), pos_hint={'center_x': 0.5, 'y': 0.3},
                          background_color=(1, 1, 1, 1))
        button_1 = Button(background_normal= "resources/button/back_menu.png",
                          background_down="resources/button/back_menu.png",
                          border=(0, 0, 0, 0),
                          size_hint=(0.25, 0.12), pos_hint={'x': 0.1, 'y': 0.2},
                          background_color=(1, 1, 1, 1))
        button_2 = Button(background_normal= "resources/button/replay.png",
                          background_down="resources/button/replay.png",
                          border=(0, 0, 0, 0),
                          size_hint=(0.25, 0.12), pos_hint={'x': 0.6, 'y': 0.2},
                          background_color=(1, 1, 1, 1))
        button_0.bind(on_press=self.on_button_0_click)
        button_1.bind(on_press=self.on_button_1_click)  # 绑定按钮事件，点击时关闭弹窗
        button_2.bind(on_press=self.on_button_2_click)
        layout.add_widget(info_image)
        layout.add_widget(message_label)
        layout.add_widget(button_0)
        layout.add_widget(button_1)
        layout.add_widget(button_2)
        # 设置弹窗内容
        self.add_widget(layout)

    def on_button_0_click(self, instance):
        # 执行回调函数（如果有）
        if self.callback_0:
            self.callback_0()
        # 关闭弹窗
        self.dismiss()
    def on_button_1_click(self, instance):
        # 执行回调函数（如果有）
        if self.callback_1:
            self.callback_1()
        # 关闭弹窗
        self.dismiss()

    def on_button_2_click(self, instance):
        if self.callback_2:
            self.callback_2()
        # 关闭弹窗
        self.dismiss()

class CustomPopup(ModalView):
    def __init__(self, image_source, button_text_1, text="look look", callback_1=None,callback_2=None,is_share=False,adMob=None, **kwargs):
        super().__init__(**kwargs)
        # 设置 ModalView 背景为透明
        self.background_color = (0, 0, 0, 0)  # 透明背景
        self.allow_stretch=True
        self.keep_ratio=False
        self.size_hint = (0.8, 0.4)
        # self.size = size  # 设置弹窗的宽高
        self.callback_1=callback_1
        self.callback_2 = callback_2
        self.is_share=is_share
        self.auto_dismiss=False
        # 创建一个 FloatLayout 来允许控件自由定位
        layout = FloatLayout()
        bg_image_source=r"resources/background/frame.png"
        video_image_source=r"resources/button/ads_button.png"
        # 创建一个 Image 组件加载自定义美术素材作为背景
        bg_image = Image(source=bg_image_source, size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5},allow_stretch=True,keep_ratio=False)
        layout.add_widget(bg_image)

        info_image=Image(source=image_source, size_hint=(0.48, 0.48), pos_hint={'center_x': 0.5, 'center_y': 0.6},allow_stretch=True)

        message_label=Label(text=text,color=(0, 0, 0, 1), size_hint=(0.3, 0.05), pos_hint={'center_x': 0.5, 'center_y': 0.33})
        # 创建一个 Button，将它放置在图片上
        button_1 = Button(text=button_text_1, size_hint=(0.3, 0.15), pos_hint={'x': 0.1, 'y': 0.1},color=(0, 0, 0, 1), background_normal="resources/button/button_g.png",border=(0, 0, 0, 0))
        button_2 = Button(text="", size_hint=(0.3, 0.15), pos_hint={'x': 0.6, 'y': 0.1}, background_normal="resources/button/button_y.png",border=(0, 0, 0, 0))
        button_1.bind(on_press=self.on_button_1_click)  # 绑定按钮事件，点击时关闭弹窗
        button_2.bind(on_press=self.on_button_2_click)
        ad_image = Image(source=video_image_source, size_hint=(0.12, 0.1), pos_hint={'center_x': 0.75, 'center_y': 0.18},
                         allow_stretch=True, keep_ratio=False)

        layout.add_widget(info_image)
        layout.add_widget(message_label)
        layout.add_widget(button_1)
        layout.add_widget(button_2)
        layout.add_widget(ad_image)
        # 设置弹窗内容
        self.add_widget(layout)

        if adMob:
            self.admob=adMob
    def on_button_1_click(self, instance):
        # 执行回调函数（如果有）
        if self.callback_1:
            self.callback_1()
        # 关闭弹窗
        self.dismiss()
    def on_button_2_click(self, instance):
        if (platform == 'win'):
            self.callback_2()
            App.get_running_app().sm.get_screen("game").level_instance.start_process()
        # 执行回调函数（如果有）
        if (platform == 'android') and (not self.is_share):
            if not self.admob.if_load_rewarded_ad():
                self.admob.load_ads()
                self.callback_2()
                return
            if self.callback_2:
                self.callback_2()
        elif (platform == 'android') and self.is_share:
            App.get_running_app().sm.get_screen("game").level_instance.set_task_complete()
            App.get_running_app().sm.get_screen("menu").player_info['money'] += 20
            self.callback_2()

        # 关闭弹窗
        self.dismiss()


class GuidePopup(ModalView):
    def __init__(self, image_source, button_text, callback=None, **kwargs):
        super().__init__(**kwargs)
        # 设置 ModalView 背景为透明
        self.background_color = (1, 0, 0, 1)  # 透明背景
        self.size_hint = (1, 1)
        self.callback = callback

        # 创建一个 FloatLayout 来允许控件自由定位
        layout = FloatLayout(size_hint=(1, 1))

        # 创建一个 Image 组件加载自定义美术素材作为背景
        guide_image = Image(source=image_source, size_hint=(1, 1), pos_hint={'x': 0, 'y': 0}, allow_stretch=True,keep_ratio=False)
        layout.add_widget(guide_image)
        # message_label = Label(text=text, color=(0, 0, 0, 1), size_hint=(0.4, 0.15),text_size=self.size,
        #                       pos_hint={'center_x': 0.5, 'center_y': 0.3})
        # 创建一个 Button，将它放置在图片上
        button = Button(text=button_text,background_normal="resources/button/button_y.png",color=(0, 0, 0, 1),
                        border=(0, 0, 0, 0), size_hint=(0.35, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.15})
        button.bind(on_press=self.on_button_click)
        # layout.add_widget(message_label)
        layout.add_widget(button)

        # 设置弹窗内容
        self.add_widget(layout)

    def on_button_click(self, instance):
        # 执行回调函数（如果有）
        if self.callback:
            self.callback()
        # 关闭弹窗
        self.dismiss()

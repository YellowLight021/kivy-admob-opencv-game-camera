import random
import time
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.utils import platform
from kivy.uix.scrollview import ScrollView
from config import CHARACTER_SIZE_FACTOR,MAX_FACE_MISS,AD_GET_COIN_FACTOR,AD_LEVEL
from generateScene import generate_challege_2_scene

from hintLabel import HintLabel,HintAnimateImage,CustomPopup


from pve import PVE
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.graphics.texture import Texture
from kivy.properties import ListProperty


class Challege_2(PVE):
    #目前同一个时刻只支持一个动作默认姿态是互斥的，但是后续可能会扩展所以先这么干申请list类型
    gesture = ListProperty([0, 0])
    #level表示第几个关卡
    def __init__(self,player_info,detector, **kwargs):
        super(Challege_2, self).__init__(player_info,detector,**kwargs)
        self.current_score=0
        self.rank=0
        self.remove_widget(self.pos_label)

    def update_rank(self,dt):
        self.rank+=1
        for monster in self.monsters:
            if hasattr(monster,"rank"):
                monster.set_rank(self.rank)

    def create_scene(self):
        layout, character,self.scene_w,self.scene_h=generate_challege_2_scene(self.monsters,self.floor_elements,self.buffs,self.coins,self.player_info)
        scroll_view = ScrollView(size=(self.device_window_width, self.device_window_height))
        scroll_view.add_widget(layout)
        return scroll_view, layout, character

    def start_process(self):
        Clock.schedule_once(self.update_rank,0.5)
        Clock.schedule_interval(self.update_rank, 120)

        Clock.schedule_interval(self.update, 1 / 30)
        Clock.schedule_interval(self.updateCamera, 1 / 8)
        for monster in self.monsters:
            monster.start_animation()
        self.is_pause=False

    def show_guide(self,dt):
        pass
    def pause_process(self):
            # 解除定时器绑定
        Clock.unschedule(self.update_rank)
        Clock.unschedule(self.update)
        Clock.unschedule(self.updateCamera)
        for monster in self.monsters:
            monster.pause_animation()
        self.is_pause = True
    def create_enemy_info(self):
        enemy_icon=Image(
            source="resources/button/star.png",# 设置背景图路径
            size_hint=(0.07, 0.035),
            pos_hint={"x": 0.85, "center_y": 0.825})
        enemy_num_label = Label(text=f"30",
                          size_hint=(0.2, 0.1),
                          pos_hint={"x": 0.85, "center_y": 0.825},
                          color=(0, 0, 0, 1),)
        return enemy_icon,enemy_num_label

    def check_status(self):
        self.current_score=self.points//10
        if self.character.health<=0:
            self.pause_process()
            print("popup=======================")
            self.new_get_coins+=self.current_score//5
            self.player_info["challege_2_score"]=max(self.current_score,self.player_info["challege_2_score"])
            message = self.language.get_string("ad reward tip").format(self.new_get_coins * AD_GET_COIN_FACTOR)
            button_text_1 = self.language.get_string("continue")
            button_text_2 = self.language.get_string("more coin")
            if (platform == 'android') and self.player_info["challenge_level"] >= AD_LEVEL:
                App.get_running_app().adMob.reward_context = f"coin:{self.new_get_coins * AD_GET_COIN_FACTOR}"
                print("=======")
                print(App.get_running_app().adMob.reward_context)
                print("=======")
                popup = CustomPopup(r"resources/button/coin_reward.png", button_text_1=button_text_1,
                                    text=message, callback_1=self.set_task_complete,
                                    callback_2=App.get_running_app().adMob.show_rewarded_ad,
                                    adMob=App.get_running_app().adMob)
            elif (platform == 'android') and self.player_info["challenge_level"] < AD_LEVEL:
                message = self.language.get_string("share reward tip").format(20)
                popup = CustomPopup(r"resources/button/coin_reward.png", button_text_1=button_text_1,
                                    text=message, callback_1=self.set_task_complete,
                                    callback_2=App.get_running_app().shareManager.start_share, is_share=True)
            else:
                popup = CustomPopup(r"resources/button/coin_reward.png", button_text_1=button_text_1, text=message,
                                    callback_1=self.set_task_complete,
                                    callback_2=self.set_task_complete)
            popup.open()

    def set_task_complete(self):
        print("set task is complte")
        self.player_info["challege_2_score"]=max(self.player_info["challege_2_score"],self.current_score)
        self.task_complete = True


    def update_position_label(self):
        level = self.player_info["challenge_level"]
        # self.pos_label.text = self.language.get_string("pve info").format(level)
        self.enemy_num_label.text=str(self.current_score)
        self.fps_label.text = f"fps:{Clock.get_fps():.2f}"



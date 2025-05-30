import random
import time
from kivy.app import App

from kivy.uix.image import Image
from kivy.utils import platform
from kivy.uix.scrollview import ScrollView
from config import CHARACTER_SIZE_FACTOR,MAX_FACE_MISS,AD_GET_COIN_FACTOR,AD_LEVEL
from generateScene import generate_challege_1_scene

from pve import PVE

from hintLabel import HintLabel,HintAnimateImage,CustomPopup

from monster import create_monster,generate_challege_1_monster
from floor import create_floor


from kivy.clock import Clock

from kivy.uix.label import Label

from kivy.properties import ListProperty


class Challege_1(PVE):
    #目前同一个时刻只支持一个动作默认姿态是互斥的，但是后续可能会扩展所以先这么干申请list类型
    gesture = ListProperty([0, 0])
    #level表示第几个关卡
    def __init__(self,player_info,detector, **kwargs):
        super(Challege_1, self).__init__(player_info,detector,**kwargs)

        self.generate_floor_count=0
        self.generate_in_cd=False
        self.current_score=0
        self.velocity_list=[(0,-0.0012*self.device_window_height),
                                   (0,-0.0024*self.device_window_height)
                                   ]
        self.if_fast=True
        self.remove_widget(self.pos_label)

    def create_scene(self):

        layout, character,self.scene_w,self.scene_h=generate_challege_1_scene(self.monsters,self.floor_elements,self.buffs,self.coins,self.player_info)
        scroll_view = ScrollView(size=(self.device_window_width, self.device_window_height))
        scroll_view.add_widget(layout)
        return scroll_view, layout, character

    def start_process(self):
        Clock.schedule_once(self.reset_floor_velocity,0.5)
        Clock.schedule_interval(self.reset_floor_velocity, 30)
        Clock.schedule_interval(self.generate_floor_monster, 4)

        Clock.schedule_interval(self.update, 1 / 30)
        Clock.schedule_interval(self.updateCamera, 1 / 8)
        for monster in self.monsters:
            monster.start_animation()
        self.is_pause=False

    def show_guide(self,dt):
        pass
    def pause_process(self):
            # 解除定时器绑定
        Clock.unschedule(self.reset_floor_velocity)
        Clock.unschedule(self.generate_floor_monster)
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

    def generate_floor_monster(self,dt):
        if not self.generate_in_cd or self.if_fast:
            self.generate_floor_count+=1
            floor_size=(random.uniform(0.3,0.5)*self.device_window_width,
                                         random.uniform(0.025,0.05)*self.device_window_height)

            floor_pos=((random.uniform(0,0.2)+self.generate_floor_count%2*0.55)*self.device_window_width,
                                             random.uniform(1,1.02)*self.device_window_height)

            new_floor=create_floor("ground_move",pos=floor_pos,
                                   size=floor_size)
            new_floor.set_velocity(self.velocity_list[self.if_fast])
            new_monster=generate_challege_1_monster(self.generate_floor_count,pos=(new_floor.center_x,new_floor.top))
            self.floor_elements.append(new_floor)
            self.layout.add_widget(new_floor)
            if new_monster:
                self.monsters.append(new_monster)
                # self.layout.add_widget(new_monster)
                new_monster.start_animation()
            #积分暂定为这个floor数量
            self.current_score=self.generate_floor_count
        self.generate_in_cd=not self.generate_in_cd

    def reset_floor_velocity(self,dt):
        self.if_fast= not self.if_fast
        for floor in self.floor_elements:
            if hasattr(floor,"velocity_y"):
                floor.set_velocity(self.velocity_list[self.if_fast])

    def check_status(self):
        if self.character.health<=0:
            self.pause_process()
            print("popup=======================")
            self.new_get_coins+=self.generate_floor_count//5
            self.player_info["challege_1_score"] = max(self.current_score, self.player_info["challege_1_score"])
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


    def update_position_label(self):
        self.enemy_num_label.text=str(self.current_score)
        self.fps_label.text = f"fps:{Clock.get_fps():.2f}"




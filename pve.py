import time
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.utils import platform
from kivy.uix.scrollview import ScrollView
from config import CHARACTER_SIZE_FACTOR,MAX_FACE_MISS,AD_GET_COIN_FACTOR,AD_LEVEL,GUIDE_LEVELS
from generateScene import generate_scene
from faceDetection import FaceDetection
from control import Controler
from faceModel.tfTypes import Colors
from hintLabel import HintLabel,HintAnimateImage,CustomPopup,GuidePopup
from coin import Coin
from buff import create_buff

from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.graphics.texture import Texture
from kivy.properties import ListProperty

import numpy as np
import os
import cv2
class PVE(FloatLayout):
    #目前同一个时刻只支持一个动作默认姿态是互斥的，但是后续可能会扩展所以先这么干申请list类型
    gesture = ListProperty([0, 0])
    #level表示第几个关卡
    def __init__(self,player_info,detector, **kwargs):
        super(PVE, self).__init__(**kwargs)
        self.device_window_width, self.device_window_height = Window.size
        self.Character_size=(CHARACTER_SIZE_FACTOR[0]*self.device_window_width,CHARACTER_SIZE_FACTOR[1]*self.device_window_height)
        self.face_miss_time=0
        self.task_complete=False
        self.character_dead = False
        self.detect_faces=detector
        self.language = App.get_running_app().language
        self.player_info=player_info
        self.controler=Controler()
        self.camera_image = self.create_face_image()
        #init elements
        self.floor_elements=[]
        self.monsters=[]
        self.buffs=[]
        self.coins = []
        self.bullets = []
        self.monster_bullets=[]
        #
        self.scroll_view, self.layout, self.character = self.create_scene()
        self.pos_label = self.create_position_label()
        self.fps_label=self.create_fps_label()
        self.enemy_img,self.enemy_num_label=self.create_enemy_info()
        self.add_widget(self.scroll_view)
        self.add_widget(self.pos_label)
        self.add_widget(self.fps_label)
        self.add_widget(self.enemy_img)
        self.add_widget(self.enemy_num_label)
        self.add_widget(self.camera_image)
        self.start()

    def start(self):
        #gesture call
        self.bind(gesture=self.gesture_change)
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)
        self.is_pause=True
        self.gesture_pre_value=0
        self.new_get_coins = 5
        self.points=0
        if self.player_info["challenge_level"]<=5 or self.player_info["challenge_level"] in GUIDE_LEVELS:
            Clock.schedule_once(self.show_guide,0.1)
        if self.player_info["challenge_level"] in GUIDE_LEVELS:
            self.pre_guide()
        else:
            self.start_process()

    def pre_guide(self):
        if self.player_info["challenge_level"]==GUIDE_LEVELS[0]:
            popup=GuidePopup(image_source=r"resources/guide/pre_guide_shake.png",button_text=self.language.get_string("continue"),
                             callback=self.start_process)
        elif self.player_info["challenge_level"]==GUIDE_LEVELS[1]:
            popup = GuidePopup(image_source=r"resources/guide/pre_guide_turn.png", button_text=self.language.get_string("continue"),
                               callback=self.start_process)
        else:
            popup = GuidePopup(image_source=r"resources/guide/pre_guide_up.png", button_text=self.language.get_string("continue"),
                               callback=self.start_process)
        popup.open()
    def create_scene(self):

        layout, character,self.scene_w,self.scene_h,self.door=generate_scene(self.monsters,self.floor_elements,self.buffs,self.coins,self.player_info)
        scroll_view = ScrollView(size=(self.device_window_width, self.device_window_height))
        scroll_view.add_widget(layout)
        return scroll_view, layout, character
    def set_cap(self,cap):
        self.cap=cap
    def start_process(self):
        Clock.schedule_interval(self.update, 1 / 30)
        Clock.schedule_interval(self.updateCamera, 1 / 8)
        for monster in self.monsters:
            monster.start_animation()
        self.is_pause=False


    def pause_process(self):
            # 解除定时器绑定
        Clock.unschedule(self.update)
        Clock.unschedule(self.updateCamera)
        for monster in self.monsters:
            monster.pause_animation()
        self.is_pause = True

    def show_guide(self,dt):
        if self.player_info["challenge_level"]==1:
            self.show_image_hint("resources/guide/shake_right",if_once=True)
            self.show_hint(self.language.get_string("keep right"),color=(0, 0, 0, 1),
                           size=(self.device_window_width*0.85, self.device_window_height*0.35))
        elif self.player_info["challenge_level"]==2:
            self.show_image_hint("resources/guide/shake_left",if_once=True)
            self.show_hint(self.language.get_string("keep left"),color=(0, 0, 0, 1),
                           size=(self.device_window_width*0.85, self.device_window_height*0.35))
        elif self.player_info["challenge_level"]==GUIDE_LEVELS[0]:
            self.show_image_hint("resources/guide/shake_right")
            self.show_hint(self.language.get_string("camera tilt"),color=(0, 0, 0, 1),
                           size=(self.device_window_width*0.8, self.device_window_height*0.32))
        elif self.player_info["challenge_level"]==GUIDE_LEVELS[1]:
            self.show_image_hint("resources/guide/turn_left")
            self.show_hint(self.language.get_string("camera rotate"),color=(0, 0, 0, 1),
                           size=(self.device_window_width*0.8, self.device_window_height*0.32))
        elif self.player_info["challenge_level"]==GUIDE_LEVELS[2]:
            self.show_image_hint("resources/guide/up")
            self.show_hint(self.language.get_string("camera retraction"),color=(0, 0, 0, 1),
                           size=(self.device_window_width*0.8, self.device_window_height*0.32))

    def show_image_hint(self,image_source,if_once=False,fps=1):
        hint = HintAnimateImage(image_source=image_source, fps=fps,
                         size=(self.device_window_width*0.3, self.device_window_height*0.15),if_once=if_once)
        hint.show(self)

    def show_hint(self, message, size,duration=15,color=(1, 0, 0, 1)):
        """显示提示文字"""
        hint = HintLabel(message=message, duration=duration,color=color,size=size)
        hint.show(self)
    def create_face_image(self):
        face_image=Image(size_hint=(0.25, 0.15),pos_hint={"x": 0.01, "center_y": 0.88},keep_ratio=False,allow_stretch=True )
        return face_image


    def create_position_label(self):
        level=self.player_info["challenge_level"]
        pos_label = Label(text=f"第{level}关，剩余怪物: {self.character.pos}",
                          size_hint=(0.45, 0.1),
                          pos_hint={"center_x": 0.5, "center_y": 0.9},
                          color=(0, 0, 0, 1),)

        # 为Label添加半透明背景图
        with pos_label.canvas.before:
            Color(1, 1, 1, 0.5)  # 半透明白色背景，调整透明度
            pos_label.rect = Rectangle(
                source="resources/button/label.png",
                pos=pos_label.pos,
                size=pos_label.size,
            )

        # 确保Label大小和位置更新时背景图同步
        def update_background(*args):
            pos_label.rect.pos = pos_label.pos
            pos_label.rect.size = pos_label.size

        pos_label.bind(size=update_background, pos=update_background)
        return pos_label

    def create_enemy_info(self):
        enemy_icon=Image(
            source="resources/button/enemy.png",# 设置背景图路径
            size_hint=(0.07, 0.035),
            pos_hint={"x": 0.85, "center_y": 0.825})
        enemy_num_label = Label(text=f"30",
                          size_hint=(0.2, 0.1),
                          pos_hint={"x": 0.85, "center_y": 0.825},
                          color=(0, 0, 0, 1),)
        return enemy_icon,enemy_num_label
    # def create_money_info(self):
    #     enemy_icon=Image(
    #         source="resources/button/enemy.png",# 设置背景图路径
    #         size_hint=(0.07, 0.035),
    #         pos_hint={"x": 0.85, "center_y": 0.87})
    #     enemy_num_label = Label(text=f"300",
    #                       size_hint=(0.2, 0.1),
    #                       pos_hint={"x": 0.85, "center_y": 0.87},
    #                       color=(0, 0, 0, 1),)
    #     return enemy_icon,enemy_num_label
    def create_fps_label(self):
        fps_label = Label(text=f"fps: {self.character.pos}",
                          size_hint=(0.2, 0.1),
                          pos_hint={"x": 0.8, "y": 0.85},
                          color=(1, 0, 0, 0),)
        return fps_label

    def calculate_initial_position(self):
        initial_x = (self.device_window_width - self.Character_size[0]) / 2
        initial_y = (self.device_window_height - self.Character_size[1]) / 2
        return initial_x, initial_y

    def gesture_change(self,_,__):
        self.controler.on_gesture(self.character,self.gesture)
    def on_key_down(self, window, key, *args):
        #这里测试跳关卡
        if (platform == 'win'):
            self.task_complete = True
        self.controler.on_key_down(self.character, key)

    def on_key_up(self, window, key, *args):

        self.controler.on_key_up(self.character, key)

    def updateCamera(self,dt):
        self.upate_face_image()

    def update(self, dt):
        self.character.update(self.floor_elements,self.buffs,self.coins,self.bullets,(self.scene_w,self.scene_h))
        self.update_position_label()

        self.update_scroll()
        #新增floor的变化
        for floor in self.floor_elements:
            floor.update()
            if floor.top<=0:
                self.floor_elements.remove(floor)
                self.layout.remove_widget(floor)
        for monster in self.monsters:
            if abs(self.character.center_x-monster.center_x)<=2*self.device_window_width and abs(self.character.center_y-monster.center_y)<=self.device_window_height:
                monster.update(self.floor_elements,self.monster_bullets,self.character,self.monsters,(self.scene_w,self.scene_h))
            if monster.health<=0:
                if monster.drop_coin:
                    new_coin=Coin(monster.pos)
                    self.coins.append(new_coin)
                    self.layout.add_widget(new_coin)
                if monster.drop_buff:
                    new_buff=create_buff("random",pos=monster.pos)
                    self.buffs.append(new_buff)
                    self.layout.add_widget(new_buff)
                self.points+=monster.point
                self.monsters.remove(monster)
                self.layout.remove_widget(monster)
            elif not monster.parent:
                self.layout.add_widget(monster)

        for bullet in self.bullets[:]:
            if bullet.update(self.monsters,self.floor_elements,(self.scene_w,self.scene_h),self.bullets):
                if bullet.parent:  # 检查子弹是否已经有父级
                    bullet.parent.remove_widget(bullet)  # 从当前父级中移除子弹
                self.layout.add_widget(bullet)  # 添加子弹到布局中
            else:
                self.bullets.remove(bullet)  # 删除出界的子弹
                self.layout.remove_widget(bullet)

        for monster_bullet in self.monster_bullets[:]:
            if monster_bullet.update([self.character],self.floor_elements,(self.scene_w,self.scene_h),self.monster_bullets):
                if monster_bullet.parent:  # 检查子弹是否已经有父级
                    monster_bullet.parent.remove_widget(monster_bullet)  # 从当前父级中移除子弹
                self.layout.add_widget(monster_bullet)  # 添加子弹到布局中
            else:
                self.monster_bullets.remove(monster_bullet)  # 删除出界的子弹
                self.layout.remove_widget(monster_bullet)

        for buff in self.buffs[:]:
            if buff.touched:
                self.layout.remove_widget(buff)
                self.buffs.remove(buff)
        for coin in self.coins[:]:
            if coin.touched:
                self.new_get_coins+=coin.add_value
                self.player_info["money"]+=coin.add_value
                self.layout.remove_widget(coin)
                self.coins.remove(coin)

        self.check_status()


    def check_status(self):
        if self.character.collides_with_door(self.door) and len(self.monsters)<=0:
            self.pause_process()
            print("popup=======================")
            message = self.language.get_string("ad reward tip").format(self.new_get_coins*AD_GET_COIN_FACTOR)
            button_text_1=self.language.get_string("continue")
            button_text_2 = self.language.get_string("more coin")
            if (platform == 'android') and self.player_info["challenge_level"]>=AD_LEVEL:
                App.get_running_app().adMob.reward_context=f"coin:{self.new_get_coins*AD_GET_COIN_FACTOR}"
                print("=======")
                print(App.get_running_app().adMob.reward_context)
                print("=======")
                popup = CustomPopup(r"resources/button/coin_reward.png", button_text_1=button_text_1,
                                    text=message,callback_1=self.set_task_complete,
                                    callback_2=App.get_running_app().adMob.show_rewarded_ad,adMob=App.get_running_app().adMob)
            elif (platform == 'android') and self.player_info["challenge_level"]<AD_LEVEL:
                message = self.language.get_string("share reward tip").format(20)
                popup = CustomPopup(r"resources/button/coin_reward.png", button_text_1=button_text_1,
                                    text=message, callback_1=self.set_task_complete,
                                    callback_2=App.get_running_app().shareManager.start_share,is_share=True)
            else:
                popup = CustomPopup(r"resources/button/coin_reward.png", button_text_1=button_text_1,text=message,
                                    callback_1=self.set_task_complete,
                                    callback_2=self.set_task_complete)
            popup.open()
            # self.task_complete = True
        # print("health:{} is_dead:{}".format(self.character.health,self.character_dead))
        if self.character.health<=0:
            self.pause_process()
            if self.character.remain_revive_times>0:
                admessage=self.language.get_string("revive_tip").format(self.character.remain_revive_times)
                button_text_1=self.language.get_string("back")
                button_text_2=self.language.get_string("revive")
                if (platform == 'android'):
                    App.get_running_app().adMob.reward_context="revive:1"
                    popup = CustomPopup(r"resources/button/heart.png",button_text_1=button_text_1
                                        ,text=admessage,callback_1=self.set_character_dead,
                                callback_2=App.get_running_app().adMob.show_rewarded_ad,adMob=App.get_running_app().adMob)
                else:
                    popup = CustomPopup(r"resources/button/heart.png",button_text_1=button_text_1,
                                        text=admessage,callback_1=self.set_character_dead,
                                callback_2=self.revive_charater)
                popup.open()
            else:
                self.set_character_dead()

    def set_task_complete(self):
        print("set task is complte")
        self.task_complete = True
    def revive_charater(self):
        self.character.revive()
    def set_character_dead(self):
        self.character_dead = True
    def upate_face_image(self):
        ret, frame = self.cap.read()
        if ret:
            # try:
                # 获取图像的像素数据并转为 OpenCV 格式
                if platform!="win":
                    frame=cv2.rotate(frame,cv2.ROTATE_90_COUNTERCLOCKWISE)
                else:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                img_bgr = cv2.flip(frame, 1)
                # img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2BGR)
                # start_time=time.time()
                faces = self.detect_faces(img_bgr)
                # print("cost time :{}".format(time.time()-start_time))
                if not len(faces):
                    self.face_miss_time+=1
                    if self.face_miss_time>=MAX_FACE_MISS:
                        self.show_hint(self.language.get_string("face loss"),size=(300, 50),duration=3)
                    new_value=0
                else:
                    self.face_miss_time =0
                    # print("{} faces were found".format(len(faces)))
                    # 这一段是给到显示的
                    render_data = FaceDetection.detections_to_render_data(faces[0:1], bounds_color=Colors.GREEN,
                                                                          keypoint_color=Colors.RED)
                    img_bgr, new_value = FaceDetection.render_to_image(render_data, img_bgr)
                # 将处理后的图像数据重新设置为 Kivy 纹理
                new_texture = Texture.create(size=(img_bgr.shape[1], img_bgr.shape[0]), colorfmt='rgb')
                new_texture.blit_buffer(img_bgr.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
                new_texture.flip_vertical()

                # 将处理后的纹理赋值给 Image 小部件
                self.camera_image.texture = new_texture
                # new_value=FaceDetection.getsture_recognize(face_pos)
                if new_value!=0:
                    #在抬头或低头的情况下如果上一个动作也是抬头获低头则不更新
                    # if self.gesture_pre_value==1 or self.gesture_pre_value==6:
                    #     self.gesture_pre_value = new_value
                    # elif self.gesture_pre_value!=new_value:
                    #这里强行让仰头动作可以连续触发
                    if self.gesture_pre_value==1 and new_value==1:
                        new_value=7
                    if self.gesture_pre_value!=new_value:
                        self.gesture_pre_value = new_value
                        self.gesture[0]=new_value
                        self.update_player_info(new_value)
                    # elif self.gesture_pre_value==1:
                    #     self.gesture[0]=7

        else:
            self.show_hint(self.language.get_string("camera open"),size=(300, 50))



            # except Exception as e:
            #     print(f"更新纹理时出错: {e}")  # 错误处理
    def update_position_label(self):
        level = self.player_info["challenge_level"]
        self.pos_label.text = self.language.get_string("pve info").format(level)
        self.enemy_num_label.text=str(len(self.monsters))
        self.fps_label.text = f"fps:{Clock.get_fps():.2f}"

    def update_player_info(self,new_value):
        if new_value==1:
            self.player_info["retraction"]+=1
        elif new_value==2 or new_value==3:
            self.player_info["tilt"] += 1
        elif new_value==4 or new_value==5:
            self.player_info["rotation"] += 1

    # def update_level_task_statu(self):
    #     if len(self.monsters)<1:
    #         self.task_complete = True

    def update_scroll(self):
        character_center_x = self.character.pos[0] + self.Character_size[0] / 2
        character_center_y = self.character.pos[1] + self.Character_size[1] / 2
        scroll_x = character_center_x - self.device_window_width / 2
        scroll_y = character_center_y - self.device_window_height / 2
        scroll_x = max(0, min(scroll_x, self.scene_w - self.device_window_width))
        scroll_y = max(0, min(scroll_y, self.scene_h - self.device_window_height))
        self.scroll_view.scroll_x = scroll_x / (self.scene_w - self.device_window_width)
        self.scroll_view.scroll_y = scroll_y / (self.scene_h - self.device_window_height)

    def cleanup(self):
        # self.pause_proess()

        # 解绑键盘事件
        Window.unbind(on_key_down=self.on_key_down)
        Window.unbind(on_key_up=self.on_key_up)

        # 清理子弹、怪物等元素
        for bullet in self.bullets:
            if bullet.parent:
                bullet.parent.remove_widget(bullet)
        for monster_bullet in self.monster_bullets:
            if monster_bullet.parent:
                monster_bullet.parent.remove_widget(monster_bullet)
        for monster in self.monsters:
            if monster.parent:
                monster.parent.remove_widget(monster)
        for floor in self.floor_elements:
            if floor.parent:
                floor.parent.remove_widget(floor)
        for buff in self.buffs:
            if buff.parent:
                buff.parent.remove_widget(buff)
        for coin in self.coins:
            if coin.parent:
                coin.parent.remove_widget(coin)
        self.bullets.clear()
        self.monsters.clear()
        self.monster_bullets.clear()
        self.floor_elements.clear()
        self.coins.clear()
        self.buffs.clear()
        # 移除场景中的其他 widget
        self.clear_widgets()
        # self.cap.clear()

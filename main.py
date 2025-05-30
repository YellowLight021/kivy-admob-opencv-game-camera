# main.py
import random

from kivy.app import App
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.modalview import ModalView
from kivy.graphics import Line,Color,Rectangle
from kivy.properties import NumericProperty, StringProperty
from kivy.animation import Animation
import os
import json
import cv2
from pve import PVE
from guidePve import GUIDE_PVE
from challege_1 import Challege_1
from challege_2 import Challege_2
from faceDetection import FaceDetection
from control import Controler
from faceModel.tfTypes import Colors
from hintLabel import HintLabel,PausePopup,GuidePopup
from kivy.core.audio import SoundLoader
from kivy.graphics import Rectangle
from plyer import storagepath
from kivy.core.window import Window
from kivy.config import Config
from threading import Thread
from kivy.logger import Logger

from config import LIMIT_LEVEL,GUIDE_LEVELS,AD_LEVEL,REVIEW_SKIN_NUM,SHARE_LEVEL,SPECIAL_CODE,CHALLEGE_LEVEL_LIMIT,CHALLEGE_OPEN_STATUS
from language import LangManager
from imageAnimation import MovingImage
from functools import partial
Config.set('graphics', 'maxfps', 30)
Config.set('graphics', 'vsync', '1')

if (platform == 'android'):
    # Get path to internal Android Storage
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission
    from jnius import autoclass


    # Specify the required android permissions here.
    request_permissions([
        Permission.CAMERA,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE
    ])


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.moving_image = None  # 动态加载的图片实例
        self.boss_frame_index=0
        self.show_boss_speak= False
        self.boss_speak_interval=10

        self.boss_resources=r"resources/monster/bigghostmonster"
        self.boss_img_num = len(os.listdir(self.boss_resources))
        self.animations = [f"resources/monster/bigghostmonster/bigghostmonster_{i}.png" for i in range(1, self.boss_img_num + 1)]

        self.door_frame_index=0
        self.door_resurces=r"resources/door"
        self.door_img_num = len(os.listdir(self.door_resurces))
        self.door_animations = [f"resources/door/door_frame_{i}.png" for i in
                           range(0, self.door_img_num)]

        self.fake_key_listen=""

    def update_info_show(self):
        if self.player_info.get('current_level', 1) == 0 and self.fake_key_listen == SPECIAL_CODE:
            print("activate special key.......")
            self.player_info['current_level']=LIMIT_LEVEL
            self.player_info['money']=9999
        self.guide_click()
        self.ask_review()
        self.check_update()
        self.check_version_update()
        self.check_gesture_open()
        self.language=App.get_running_app().language
        self.ids.player_level.text = str(self.player_info.get('current_level', 1))
        self.ids.player_money.text = str(self.player_info.get('money', 0))

        if self.player_info['if_music_on']:
            self.ids.music_control.background_normal = "resources/button/sound.png"
        else:
            self.ids.music_control.background_normal = "resources/button/silence.png"

        self.ids.motion_record.text=self.language.get_string("record")
        self.ids.language_type.text=self.language.get_lan()

        # self.ids.player_retraction_name.text = self.language.get_string("retraction")
        self.ids.player_retraction.text = str(self.player_info.get('retraction', 0))
        # self.ids.player_tilt_name.text = self.language.get_string("tilt")
        self.ids.player_tilt.text = str(self.player_info.get('tilt', 0))
        # self.ids.player_rotation_name.text = self.language.get_string("rotation")
        self.ids.player_rotation.text = str(self.player_info.get('rotation', 0))

        self.ids.player_avatar.source = f"resources/character/{self.player_info.get('current_skin')}.png"  # 确保头像路径正确
        self.ids.player_avatar.bind(on_touch_down=self.open_store)
        self.ids.boss_show.bind(on_touch_down=self.click_boss)
        self.ids.challege_enter.bind(on_touch_down=self.click_door)
        # 选择进入的关卡
        self.ids.current_level.text = self.language.get_string("play level").format(self.player_info.get('challenge_level', 1))

        self.level_bar = CustomProgressBar(
            pos_hint={"center_x": 0.5, "center_y": 0.38},
            size_hint=(0.5, 0.02),
            max_value=100,
            background_source='resources/background/progress_bg.png',
            progress_source='resources/background/progress.png'
        )
        self.add_widget(self.level_bar)
        self.level_bar.set_target_value(self.player_info.get("current_level", 1),2)
        self.ids.boss_process.text="{}/100".format(self.player_info.get("current_level", 1))



    def on_enter(self):
        # print("enter menu window :{}".format(Window.size))
        # print("enter menu system window :{}".format(Window.system_size))
        # 更新kv文件中的标签文本
        self.player_info = App.get_running_app().data
        if self.player_info['if_music_on']:
            App.get_running_app().play_menu_music()
        self.update_info_show()

        # App.get_running_app().save_progress(self.player_info)

        if len(App.get_running_app().cameraIds)<1:
            self.show_hint(self.language.get_string("restart tip"),9999)

        if (platform == 'android') and self.player_info.get('current_level', 1)>AD_LEVEL:
            if not App.get_running_app().adMob.banner_is_working:
                Clock.schedule_once(App.get_running_app().adMob.refresh_banner, 0)  # 立即触发一次
                Clock.schedule_interval(App.get_running_app().adMob.refresh_banner, 30)  # 然后每 30 秒触发一次
                App.get_running_app().adMob.banner_is_working=True




        Clock.schedule_interval(self.update_boss_speak,self.boss_speak_interval)
        Clock.schedule_interval(self.update_boss_image,1)
        Clock.schedule_once(self.animate_boss, 1)
        Clock.schedule_interval(self.update_door_image, 1)



    def update_boss_image(self,dt):
        self.boss_frame_index = (self.boss_frame_index + 1) % self.boss_img_num
        self.ids.boss_show.source=self.animations[self.boss_frame_index]

    def update_door_image(self,dt):
        self.door_frame_index = (self.door_frame_index + 1) % self.door_img_num
        self.ids.challege_enter.source = self.door_animations[self.door_frame_index]
    def click_boss(self,instance=None, touch=None):
        if instance.collide_point(*touch.pos):  # 判断触摸位置是否在头像上
            self.update_boss_speak(None)
    def update_boss_speak(self,dt):
        if self.show_boss_speak==False:
            if self.player_info.get("current_level", 1)>=max(GUIDE_LEVELS):
                self.ids.boss_speak.source=os.path.join("resources/button",random.choice(["speak_1.png","speak_2.png"]))
                # print(self.ids.boss_speak.resources)
                self.ids.boss_speak.opacity=1
                self.ids.boss_speak_text.color=(0, 0, 0, 1)
                self.ids.boss_speak_text.text=self.language.get_string(f"boss speak {random.randint(1,10)}")
        else:
            self.ids.boss_speak.opacity=0
            self.ids.boss_speak_text.color = (0, 0, 0, 0)
        self.show_boss_speak = not self.show_boss_speak

    def animate_boss(self, dt):
        screen_width, screen_height = Window.size
        original_size=[int(0.44 * screen_width), int(0.22* screen_height)]
        original_pos=[int(0.28 * screen_width), int(0.42 * screen_height)]

        self.ids.boss_show.size_hint=(None,None)
        self.ids.boss_show.pos_hint={}
        self.ids.boss_show.size=original_size
        self.ids.boss_show.pos=original_pos
        swing_distance = self.ids.boss_show.width * 0.2


        self.anim = Animation(pos=(original_pos[0] + swing_distance, original_pos[1]), duration=3, t='in_out_sine') + \
                    Animation(pos=(original_pos[0], original_pos[1]), duration=3, t='in_out_sine') + \
                    Animation(pos=(original_pos[0] - swing_distance, original_pos[1]), duration=3, t='in_out_sine')+ \
                    Animation(pos=(original_pos[0], original_pos[1]), duration=3, t='in_out_sine') + \
                    Animation(pos=(original_pos[0], original_pos[1] + swing_distance), duration=3, t='in_out_sine') + \
                    Animation(pos=(original_pos[0], original_pos[1]), duration=3, t='in_out_sine') + \
                    Animation(pos=(original_pos[0], original_pos[1] - swing_distance), duration=3, t='in_out_sine') + \
                    Animation(pos=(original_pos[0], original_pos[1]), duration=3, t='in_out_sine')
        self.anim.repeat=True
        self.anim.start(self.ids.boss_show)

    def stop_animate_boss(self):
        Animation.stop_all(self.ids.boss_show)

    # def show_advertisement(self):
    #     app = App.get_running_app()
    #     if hasattr(app, 'admob_manager'):
    #         # 假设广告展示方法是 show_advertisement()
    #         app.admob_manager.show_rewarded_ad()
    #     else:
    #         print("没有找到 AdMob 管理器！")
    def check_gesture_open(self):
        self.player_info["tilt_opened"] = False if self.player_info.get("current_level", 1) < GUIDE_LEVELS[0] else True
        self.player_info["rotation_opened"] = False if self.player_info.get("current_level", 1) < GUIDE_LEVELS[1] else True
        self.player_info["retraction_opened"] = False if self.player_info.get("current_level", 1) < GUIDE_LEVELS[2] else True

    def check_update(self):
        if self.player_info.get("current_level", 1)<LIMIT_LEVEL and self.player_info['if_level_final']:
            self.player_info["if_level_final"]=False
            self.player_info["current_level"] += 1
            self.player_info["challenge_level"] += 1
        if self.player_info.get("current_level", 1)>=LIMIT_LEVEL and self.player_info["if_level_final"]:
            self.ids.next_level.background_normal="resources/button/add.png"
    def check_version_update(self):
        if platform == 'android':
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            UpdateHelper = autoclass('org.test.google_update.UpdateHelper')

            activity = PythonActivity.mActivity
            UpdateHelper.checkForUpdate(activity)
        print("update checked")

    def guide_click(self):
        if self.moving_image:
            self.moving_image.stop_animation()
            self.moving_image=None

        if self.player_info.get('current_level', 1) < 1:
            self.moving_image = MovingImage(pos_factor=[0.7,0.1])
            self.add_widget(self.moving_image)  # 添加到屏幕中
        elif len(self.player_info.get("skins"))<=1 and self.player_info.get("money")>=10:
            self.moving_image = MovingImage(pos_factor=[0.25,0.85])
            self.add_widget(self.moving_image)  # 添加到屏幕中
        elif self.player_info.get("current_level")>=SHARE_LEVEL and not self.player_info.get("is_shared"):

            self.moving_image = MovingImage(pos_factor=[0.73, 0.8], if_mirror=False)
            self.add_widget(self.moving_image)  # 添加到屏幕中
        elif self.player_info.get("current_level")>=CHALLEGE_LEVEL_LIMIT["challege_1"] and not self.player_info.get("challege_1_score"):
            self.moving_image = MovingImage(pos_factor=[0.85, 0.6])
            self.add_widget(self.moving_image)  # 添加到屏幕中
        elif self.player_info.get("current_level")>=LIMIT_LEVEL and self.player_info["if_level_final"]:
            self.moving_image = MovingImage(pos_factor=[0.82, 0.22])
            self.add_widget(self.moving_image)  # 添加到屏幕中
            self.show_hint("please go to the store for update",180)
        if self.moving_image:
            # 启动动画
            Clock.schedule_once(self.moving_image.start_animation, 1)





    def previous_level(self):
        #测试广告
        # self.show_advertisement()

        if self.player_info.get('challenge_level', 1) > 0:
            self.player_info['challenge_level'] -= 1
        self.ids.current_level.text = self.language.get_string("play level").format(self.player_info.get('challenge_level', 1))

    def next_level(self):
        max_level = self.player_info.get("current_level", 1)
        if self.player_info.get('challenge_level', 1) < max_level:
            self.player_info['challenge_level'] += 1
        elif max_level>=LIMIT_LEVEL:

            self.open_google_play()
        self.ids.current_level.text = self.language.get_string("play level").format(self.player_info.get('challenge_level', 1))


    def share(self):
        self.player_info['is_shared'] = True
        App.get_running_app().save_progress(self.player_info)
        if platform=="android":
            App.get_running_app().shareManager.start_share()
    def ask_review(self):
        if (platform == 'android'):
            if (platform == 'android'):
                from jnius import autoclass, cast
                if len(self.player_info.get("skins")) >= REVIEW_SKIN_NUM:
                    # if len(self.player_info.get("skins"))>=1:

                    # 获取当前的 Activity 对象
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity

                    # 加载你定义的 Java 类（包名需与你 Java 文件保持一致）
                    ReviewHelper = autoclass('org.test.google_review.ReviewHelper')

                    # 实例化 ReviewHelper 并调用 requestReview()
                    review_helper = ReviewHelper(activity)
                    review_helper.requestReview()

    def switch_camera(self):
        app = App.get_running_app()
        current_index = app.cap_index
        if len(self.fake_key_listen)>=len(SPECIAL_CODE):
            self.fake_key_listen=""
        self.fake_key_listen+="1"
        if len(app.cameraIds)>1:
        # 获取下一个摄像头的索引
            next_index = (current_index + 1) % len(app.cameraIds)

            # 更新摄像头索引并重新打开摄像头
            app.cap_index = next_index
            # app.cap.release()
            # app.cap = cv2.VideoCapture(app.cap_index)
            # # 确保摄像头切换成功
            # if not app.cap.isOpened():
            #     self.show_hint(f"Failed to open camera {next_index}")
            # else:
            self.show_hint(self.language.get_string("switch camera").format(next_index))
        else:
            self.show_hint(self.language.get_string("only one"))

    def switch_music_state(self):
        self.player_info['if_music_on']=not self.player_info['if_music_on']
        self.update_info_show()
        App.get_running_app().save_progress(self.player_info)
        if self.player_info['if_music_on']:
            App.get_running_app().play_menu_music()
        else:
            App.get_running_app().stop_menu_music()

    def switch_language(self):
        self.player_info["language"]=self.language.switch_lan()
        if len(self.fake_key_listen)>=len(SPECIAL_CODE):
            self.fake_key_listen=""
        self.fake_key_listen += "0"
        self.update_info_show()
        App.get_running_app().save_progress(self.player_info)
    def show_motion_tip(self,motion_type_resource):
        if not self.player_info.get("tilt_opened",False) and "shake" in motion_type_resource:
            #左右移动未解锁
            self.show_hint(self.language.get_string("shake not unlocked"))
        elif not self.player_info.get("rotation_opened",False) and "turn" in motion_type_resource:
            #转向功能未解锁
            self.show_hint(self.language.get_string("turn not unlocked"))
        elif not self.player_info.get("retraction_opened",False) and "up" in motion_type_resource:
            #大跳功能未解锁
            self.show_hint(self.language.get_string("up not unlocked"))
        else:

            popup = GuidePopup(image_source=motion_type_resource,
                               button_text=self.language.get_string("continue"))
            popup.open()

    def open_google_play(self):
        print("go to the store")
        if platform == 'android':
            # 获取当前的 Activity 和 Context
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')

            # 获取应用的包名
            context = PythonActivity.mActivity
            package_name = context.getPackageName()

            try:
                # 尝试打开 Google Play 商店的应用详情页面
                uri = Uri.parse(f'market://details?id={package_name}')
                intent = Intent(Intent.ACTION_VIEW, uri)
                intent.setPackage('com.android.vending')
                context.startActivity(intent)
                print("open store")
            except Exception:
                # 如果设备上未安装 Google Play 商店，使用浏览器打开应用详情页面
                uri = Uri.parse(f'https://play.google.com/store/apps/details?id={package_name}')
                intent = Intent(Intent.ACTION_VIEW, uri)
                context.startActivity(intent)
                print("open safari")

    def open_store(self, instance=None, touch=None):
        # 判断触摸是否发生在头像区域
        if instance.collide_point(*touch.pos):  # 判断触摸位置是否在头像上
            shop_popup = StorePopup(player_info=self.player_info, menu_screen=self)  # 传递玩家信息
            shop_popup.open()

    def click_door(self, instance=None, touch=None):
        # 判断触摸是否发生在头像区域
        if instance.collide_point(*touch.pos):  # 判断触摸位置是否在头像上
            shop_popup = ChallegePopup(player_info=self.player_info, menu_screen=self)  # 传递玩家信息
            shop_popup.open()

    def on_leave(self, *args):
        # 停止菜单背景音乐
        if self.player_info['if_music_on']:
            App.get_running_app().stop_menu_music()
        # if (platform == 'android'):
        #     Clock.unschedule(App.get_running_app().adMob.refresh_banner)
        #     App.get_running_app().adMob.hide_banner()
        Clock.unschedule(self.update_boss_speak)
        Clock.unschedule(self.update_boss_image)
        self.stop_animate_boss()

    def show_hint(self, message, duration=3):
        """显示提示文字"""
        hint = HintLabel(message=message, duration=duration)
        hint.show(self)


class LevelScreen(Screen):
    pass

class GameScreen(Screen):
    def __init__(self,player_info,detector,cap_index,game_name, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self.player_info = player_info
        self.detector=detector
        
        self.cap_index=cap_index
        self.game_name=game_name

        self.wake_camera()
        if self.game_name=="pve":
            if self.player_info['challenge_level'] not in GUIDE_LEVELS:
                self.level_class = PVE
            else:
                self.level_class=GUIDE_PVE
        elif self.game_name=="challege_1":

            self.level_class=Challege_1

            # self.level_class=Challege_1
        elif self.game_name=="challege_2":

            self.level_class=Challege_2
        else:

            pass
        # self.tasks_completed = False
        Clock.schedule_interval(self.update_tasks, 1 / 10.)

    def update_tasks(self, dt):
        if self.level_instance.task_complete:
            self.player_info["block_times"] = 0
        # if self.tasks_completed:
            self.check_level_complete()
        if self.level_instance.character_dead:
            self.player_info["block_times"] += 1
            self.check_level_failed()

    def on_enter(self):
        # print("enter game window :{}".format(Window.size))
        # print("enter game system window :{}".format(Window.system_size))
        # 播放游戏界面的背景音乐
        if self.player_info['if_music_on']:
            App.get_running_app().play_game_music()

        # if (platform == 'android') and self.player_info.get('current_level', 1)>AD_LEVEL:
        #     Clock.schedule_once(App.get_running_app().adMob.refresh_banner, 0)  # 立即触发一次
        #     Clock.schedule_interval(App.get_running_app().adMob.refresh_banner, 30)  # 然后每 30 秒触发一次

    def check_level_complete(self):
        Clock.unschedule(self.update_tasks)
        if self.game_name=="pve":
            if self.player_info['challenge_level']==self.player_info["current_level"]:
                print("current_level{} {}".format(self.player_info["current_level"],LIMIT_LEVEL))
                if self.player_info["current_level"]+1>LIMIT_LEVEL:
                    self.player_info["current_level"]=LIMIT_LEVEL
                    self.player_info["if_level_final"]=True
                    App.get_running_app().save_progress(self.player_info)
                    self.return_to_menu()
                    return
                else:
                    self.player_info["current_level"] = self.player_info["current_level"]+1
                print("current_level{}".format(self.player_info["current_level"]))
                self.player_info['challenge_level']=self.player_info["current_level"]
            elif self.player_info['challenge_level']<self.player_info["current_level"]:
                self.player_info['challenge_level']+=1
            App.get_running_app().save_progress(self.player_info)
            if (platform == 'android'):
                App.get_running_app().logEventManager.log_event("level_complete",
                                                                {"current_level":self.player_info["current_level"],
                                                                 "challenge_level":self.player_info['challenge_level']})
            App.get_running_app().load_level()
        elif self.game_name=="challege_1":
            #挑战challege_1试炼内容
            self.return_to_menu()
            App.get_running_app().save_progress(self.player_info)
        elif self.game_name == "challege_2":
            # 挑战challege_1试炼内容
            self.return_to_menu()
            App.get_running_app().save_progress(self.player_info)
        elif self.game_name == "challege_3":
            # 挑战challege_1试炼内容
            self.return_to_menu()
            App.get_running_app().save_progress(self.player_info)
        elif self.game_name == "challege_4":
            # 挑战challege_1试炼内容
            self.return_to_menu()
            App.get_running_app().save_progress(self.player_info)

    def restart_level(self):
        Clock.unschedule(self.update_tasks)
        App.get_running_app().save_progress(self.player_info)
        App.get_running_app().load_level()

    def check_level_failed(self):
        Clock.unschedule(self.update_tasks)

        App.get_running_app().save_progress(self.player_info)
        self.return_to_menu()

    def on_pre_enter(self):
        self.level_instance = self.level_class(self.player_info,self.detector)
        self.add_widget(self.level_instance)

        # Clock.schedule_once(self.initialize_camera, 0)

        return_button = Button(
           # text="返回",
            background_normal="resources/button/pause.png",
            border=(0, 0, 0, 0),
            size_hint=(0.15, 0.1),
            pos_hint={"right": 1, "center_y": 0.9},
            on_release=self.pause_game
        )
        self.add_widget(return_button)
    def wake_camera(self):
        Clock.schedule_once(self.initialize_camera, 0)
    def stop_camera(self):
        if self.cap.isOpened():
            self.cap.release()
    def initialize_camera(self,instance=None):
        self.cap = cv2.VideoCapture(self.cap_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 128)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 128)
        if (platform == 'android'):
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('R', 'G', 'B', '3'))
        self.level_instance.set_cap(self.cap)

    def resume_game(self,instance=None):
        self.wake_camera()
        self.level_instance.start_process()

    def pause_game(self, instance=None):
        self.stop_camera()
        if not self.level_instance.is_pause:
            self.level_instance.pause_process()
            popup = PausePopup(f"resources/character/{self.player_info.get('current_skin')}.png",
                               text="",
                               callback_0=self.resume_game,
                               callback_1=self.check_level_failed,
                               callback_2=self.restart_level)

            popup.open()
    def return_to_menu(self, instance=None):
        # 切换到 MenuScreen
        self.manager.current = "menu"

    def on_leave(self, *args):
        # 停止所有定时器
        Clock.unschedule(self.update_tasks)
        if hasattr(self, 'level_instance'):
            self.level_instance.pause_process()
            self.level_instance.cleanup()
            self.remove_widget(self.level_instance)
        # 如果有其他动态控件或任务，确保它们也被移除或停止
        for widget in self.children[:]:
            if isinstance(widget, Button):
                self.remove_widget(widget)
        if self.player_info['if_music_on']:
            App.get_running_app().stop_game_music()
        if self.cap.isOpened():
            self.cap.release()
        # if (platform == 'android'):
        #     Clock.unschedule(App.get_running_app().adMob.refresh_banner)
        #     App.get_running_app().adMob.hide_banner()

##这里是对于

class GameApp(App):
    def build(self):
        if (platform == 'android'):
            from advertisement import AdMobManager
            self.adMob= AdMobManager()
            from share import ShareManager
            self.shareManager=ShareManager()

            from firebase import AppLogEventManager
            self.logEventManager=AppLogEventManager()
            self.logEventManager.log_event("app_open", {})

        self.menu_music = SoundLoader.load("music/bg_music_menu.wav")
        self.game_music = SoundLoader.load("music/bg_music_level.wav")
        # font_path=os.path.join(os.getcwd(), "font", "msyh.ttc")
        # LabelBase.register(name="msyh", fn_regular=font_path)
        font_path=os.path.join(os.getcwd(), "font", "Medium.ttf")
        LabelBase.register(name="msyh", fn_regular=font_path)
        model_path = os.path.join(os.getcwd(), "faceModel", "face_detection_short_range.tflite")

        self.record_path = os.path.join(self.user_data_dir, "data.json")
        # self.record_path = os.path.join(os.getcwd(),'data', "data.json")
        self.default_record_path = os.path.join(os.getcwd(),'data', "data.json")
        self.load_progress()
        self.language=LangManager(self.data.get('language',0))
        self.detect_faces = FaceDetection(model_path)
        self.check_cameras()
        if platform=="win":
            self.cap_index = self.data.get('cap_id', 0)
        else:
            self.cap_index = self.data.get('cap_id', 1)

        #不要在这里创建，进入gamescreen在创建
        # self.cap = cv2.VideoCapture(self.cap_index)
        # 创建主布局
        self.main_layout = BoxLayout(orientation='vertical')

        self.create_screen_manager()


        return self.main_layout

    def on_pause(self):
        # 应用进入后台时触发
        print("App is in background")
        if self.sm.current == "game":
            self.sm.get_screen("game").pause_game()
        # 在这里处理暂停游戏、保存状态等逻辑
        return True  # 返回 True 表示你已经处理了暂停逻辑


    def on_resume(self):
        Logger.info("kivmob_test: on_resume()")
        if platform == 'android':
            self.adMob.load_ads()

    def check_cameras(self):
        self.cameraIds=[]
        for i in range(6):
            self.tempCam = cv2.VideoCapture(i)
            if self.tempCam.isOpened():
                self.cameraIds.append(i)
                self.tempCam.release()
            else:
                self.tempCam.release()
                break

    def create_screen_manager(self):
        self.sm = ScreenManager()
        # 手动添加 MenuScreen 和 LevelScreen
        self.sm.add_widget(MenuScreen(name="menu"))
        self.sm.add_widget(LevelScreen(name="level"))

        self.sm.current = "menu"
        self.sm.size_hint_y = 1
        self.main_layout.add_widget(self.sm)


    def load_progress(self):
        with open(self.default_record_path, 'r') as file:
            default_data= json.load(file)
        if os.path.exists(self.record_path):
            with open(self.record_path, 'r') as file:
                self.data = json.load(file)
                for keyname in default_data:
                    if keyname not in self.data:
                        self.data[keyname]=default_data[keyname]
        else:
            self.data=default_data


    def save_progress(self, player_info):
        player_info["tilt_opened"] = False if player_info.get("current_level", 1) < GUIDE_LEVELS[0] else True
        player_info["rotation_opened"] = False if player_info.get("current_level", 1) < GUIDE_LEVELS[1] else True
        player_info["retraction_opened"] = False if player_info.get("current_level", 1) < GUIDE_LEVELS[2] else True
        print("save debug current level:{}".format(player_info.get('current_level', 1)))
        try:
            self.data = player_info
            with open(self.record_path, 'w') as file:
                json.dump(self.data, file)
        except Exception as e:
            Logger.error(f"Failed to save progress: {e}")

    def load_level(self):
        """加载指定关卡"""
        if self.sm.has_screen("game"):
            game_screen = self.sm.get_screen("game")

            # 清理上一关的资源
            game_screen.on_leave()  # 确保调用 on_leave 释放资源
            self.sm.remove_widget(game_screen)  # 移除上一关的屏幕

        # 创建并加载 GameScreen
        game_screen = GameScreen(player_info=self.data,detector=self.detect_faces,cap_index=self.cap_index, name="game",game_name="pve")
        self.sm.add_widget(game_screen)
        self.sm.current = "game"

    def load_challege(self,game_name):
        if self.sm.has_screen("game"):
            game_screen = self.sm.get_screen("game")

            # 清理上一关的资源
            game_screen.on_leave()  # 确保调用 on_leave 释放资源
            self.sm.remove_widget(game_screen)  # 移除上一关的屏幕

        # 创建并加载 GameScreen
        game_screen = GameScreen(player_info=self.data,detector=self.detect_faces,cap_index=self.cap_index, name="game",game_name=game_name)
        self.sm.add_widget(game_screen)
        self.sm.current = "game"

    def play_menu_music(self):
        if self.menu_music:
            self.menu_music.loop = True
            self.menu_music.play()

    def stop_menu_music(self):
        if self.menu_music:
            self.menu_music.stop()

    def play_game_music(self):
        if self.game_music:
            self.game_music.loop = True
            self.game_music.play()

    def stop_game_music(self):
        if self.game_music:
            self.game_music.stop()

class StorePopup(ModalView):
    def __init__(self, player_info, menu_screen, **kwargs):
        super(StorePopup, self).__init__(**kwargs)
        self.title = ""
        self.language = App.get_running_app().language
        self.size_hint = (0.8, 0.7)  # 弹窗大小
        self.auto_dismiss = True  # 确保点击外部时关闭弹窗
        self.player_info = player_info  # 保存玩家信息
        self.menu_screen = menu_screen  # 保存传递的MenuScreen引用
        self.background = r"resources/background/record.png"  # 设置背景图像路径
        self.create_store_ui()  # 初始化商店 UI

    def create_store_ui(self):
        """创建商店的用户界面"""
        with open("data/store.json", "r", encoding='utf-8') as file:
            self.items_data = json.load(file)

        # 创建一个垂直布局作为Popup的content
        main_layout = BoxLayout(orientation='vertical', size_hint=(1, 1))

        # 获取窗口尺寸
        screen_width, screen_height = Window.size
        money_info=FloatLayout(size_hint=(1, 0.1),pos_hint={"x": 0.1, "y": 0.9})
        # 添加显示金币的Label到布局中，设置为右上角
        self.money_img=Image(
            source="resources/money/coin/coin_1.png",# 设置背景图路径
            size_hint=(0.5, 0.5),
            pos_hint={"center_x": 0.1, "center_y": 0.5})
        self.money_label = Label(
            text=str(self.player_info['money']),
            size_hint=(0.5, 0.5),
            # size=(screen_width * 0.25, screen_height * 0.07),
            pos_hint={"x": 0.1, "center_y": 0.5},
            font_size=screen_height * 0.03,
            color=(0, 0, 0, 1)
        )

        money_info.add_widget(self.money_img)
        money_info.add_widget(self.money_label)
        main_layout.add_widget(money_info)
        # 创建 ScrollView 和 GridLayout
        scroll_view = ScrollView(size_hint=(1, 1))
        self.grid_layout = GridLayout(cols=1, padding=screen_width * 0.05, spacing=screen_height * 0.02, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        # 每5个商品一页
        for index, item in enumerate(self.items_data["items"]):
            item_button = self.create_item_button(item, screen_width, screen_height)
            self.grid_layout.add_widget(item_button)

            # Add a separator line between items
            self.add_separator(main_layout)

        scroll_view.add_widget(self.grid_layout)
        main_layout.add_widget(scroll_view)

        # 设置Popup的content为整个main_layout
        self.add_widget(main_layout)

    def add_separator(self, layout):
        """Add a black line as a separator between the widgets."""
        with layout.canvas.before:
            Color(0, 0, 0, 1)  # Set color to black
            Line(width=2, points=[0, 0, Window.width, 0])  # Draw a horizontal line

    def create_item_button(self, item, screen_width, screen_height):
        """创建商品按钮，包含商品图片、价格和购买按钮"""
        layout = GridLayout(cols=3, size_hint_y=None, height=screen_height * 0.1)

        item_image_size_hint = (0.3, 1)
        item_info_size_hint = (0.4, 1)

        item_image = Image(source=item["image"], allow_stretch = True,size_hint=item_image_size_hint)
        layout.add_widget(item_image)

        info_layout = BoxLayout(orientation='vertical', size_hint=item_info_size_hint)
        # name_label = Label(text="金币", size_hint_y=None, height=screen_height * 0.1,color=(0, 0, 0, 1))
        name_label=Image(
            source="resources/money/coin/coin_1.png",# 设置背景图路径
            size_hint=(0.25, 0.25),
            pos_hint={"center_x": 0.5, "center_y": 0.5})
        price_label = Label(text=f"{item['price']}", size_hint_y=None, height=screen_height * 0.05,color=(0, 0, 0, 1))
        info_layout.add_widget(name_label)
        info_layout.add_widget(price_label)

        buy_button = Button(size_hint=(None, None), size=(screen_width * 0.2, screen_height * 0.05),border=(0, 0, 0, 0) )

        if item["id"] in self.player_info["skins"]:
            buy_button.text = self.language.get_string("choose")
            buy_button.background_normal="resources/button/button_g.png"
            buy_button.color=(0, 0, 0, 1)
        else:
            buy_button.text = self.language.get_string("buy")
            buy_button.background_normal="resources/button/button_y.png"
            buy_button.color = (0, 0, 0, 1)

        buy_button.bind(on_release=self.on_item_button_pressed)

        buy_button.item = item
        layout.add_widget(info_layout)
        layout.add_widget(buy_button)

        return layout

    def on_item_button_pressed(self, instance):
        """处理按钮点击事件，无论是购买还是使用"""
        item = instance.item
        print(f"按钮点击，商品ID: {item['id']}, 当前金币: {self.player_info['money']}")

        if instance.text == self.language.get_string("buy"):
            if self.player_info["money"] >= item["price"]:
                self.player_info["money"] -= item["price"]
                self.player_info["skins"].append(item["id"])
                print(f"购买成功，剩余金币: {self.player_info['money']}")
                # 更新商店界面
                self.update_shop_screen()
                instance.text = self.language.get_string("choose")
                instance.background_normal = "resources/button/button_g.png"
            else:
                print("金币不足，购买失败！")

        elif instance.text == self.language.get_string("choose"):
            print(f"使用皮肤，商品ID: {item['id']}")
            self.use_skin(item)

        # 购买或使用皮肤后，更新菜单界面的信息
        self.menu_screen.update_info_show()
        App.get_running_app().save_progress(self.player_info)

    def update_shop_screen(self):
        """更新商店界面"""
        # 只更新金币Label和按钮的文本，而不是重建整个界面
        self.money_label.text = str(self.player_info['money'])
        for index, item in enumerate(self.items_data["items"]):
            for button in self.grid_layout.children:
                if hasattr(button, 'item') and button.item == item:
                    button.text = self.language.get_string("choose") if item["id"] in self.player_info["skins"] else self.language.get_string("buy")
                    button.background_normal = "resources/button/button_g.png" if item["id"] in self.player_info["skins"] else "resources/button/button_y.png"
                    break

    def use_skin(self, item):
        """使用皮肤的具体操作"""
        print(f"使用皮肤操作，商品ID: {item['id']}")
        self.player_info["current_skin"] = item["id"]

class ChallegePopup(ModalView):
    def __init__(self, player_info, menu_screen, **kwargs):
        super(ChallegePopup, self).__init__(**kwargs)
        self.title = ""
        self.language = App.get_running_app().language
        self.size_hint = (0.8, 0.6)  # 弹窗大小
        self.auto_dismiss = True  # 确保点击外部时关闭弹窗
        self.player_info = player_info  # 保存玩家信息
        self.menu_screen = menu_screen  # 保存传递的MenuScreen引用
        self.background = r"resources/background/record.png"  # 设置背景图像路径
        self.create_store_ui()  # 初始化商店 UI

    def create_store_ui(self):
        # 创建一个垂直布局作为Popup的content
        main_layout = BoxLayout(orientation='vertical', size_hint=(1, 1))

        # 获取窗口尺寸
        screen_width, screen_height = Window.size
        challege_info=FloatLayout(size_hint=(1, 0.1),pos_hint={"x": 0.1, "y": 0.9})
        # 添加显示金币的Label到布局中，设置为右上角
        self.challege_label = Label(
            text="let's challege",
            size_hint=(0.5, 0.5),
            # size=(screen_width * 0.25, screen_height * 0.07),
            pos_hint={"x": 0.1, "center_y": 0.5},
            font_size=screen_height * 0.03,
            color=(0, 0, 0, 1)
        )

        challege_info.add_widget(self.challege_label)
        main_layout.add_widget(challege_info)
        # 创建 ScrollView 和 GridLayout
        scroll_view = ScrollView(size_hint=(1, 1))
        self.grid_layout = GridLayout(cols=1, padding=screen_width * 0.05, spacing=screen_height * 0.02, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
        self.special_pve_dict={"challege_1":self.player_info["challege_1_score"],
                               "challege_2":self.player_info["challege_2_score"],
                               "challege_3":self.player_info["challege_3_score"],
                               "challege_4":self.player_info["challege_4_score"]}
        # 每5个商品一页
        for challege_name in self.special_pve_dict.keys():
            pve_enter = self.create_pve_enter(challege_name, screen_width, screen_height)
            self.grid_layout.add_widget(pve_enter)

            # Add a separator line between items
            self.add_separator(main_layout)

        scroll_view.add_widget(self.grid_layout)
        main_layout.add_widget(scroll_view)

        # 设置Popup的content为整个main_layout
        self.add_widget(main_layout)

    def add_separator(self, layout):
        """Add a black line as a separator between the widgets."""
        with layout.canvas.before:
            Color(0, 0, 0, 1)  # Set color to black
            Line(width=2, points=[0, 0, Window.width, 0])  # Draw a horizontal line

    def create_pve_enter(self, challege_name, screen_width, screen_height):
        """创建商品按钮，包含商品图片、价格和购买按钮"""
        layout = GridLayout(cols=3, size_hint_y=None, height=screen_height * 0.1)

        item_image_size_hint = (0.3, 1)
        item_button_size_hint=(0.2,1)
        enter_enable = True if (
                    self.player_info["current_level"] >= CHALLEGE_LEVEL_LIMIT[challege_name] and CHALLEGE_OPEN_STATUS[
                challege_name]) else False
        item_image = Image(source=f"resources/button/{challege_name}.png", allow_stretch = True,size_hint=item_image_size_hint)

        challege_info = Label(
            size_hint=(0.4, 1),
            color=(0, 0, 0, 1)
        )
        if enter_enable:
            challege_info.text=self.language.get_string(challege_name)
        elif not CHALLEGE_OPEN_STATUS[challege_name]:
            challege_info.text=self.language.get_string("challege_is_coming")
        else:
            challege_info.text = self.language.get_string("challege_is_limit").format(CHALLEGE_LEVEL_LIMIT[challege_name])

        button_layout = BoxLayout(orientation='vertical', size_hint=item_button_size_hint)


        enter_button = Button(size_hint=(1,0.5),border=(0, 0, 0, 0),text=self.language.get_string("start"),color=(0, 0, 0, 1))
        enter_button.background_normal = "resources/button/button_y.png" if enter_enable else "resources/button/button_g.png"
        enter_button.bind(on_release=self.on_challege_button_pressed)

        enter_button.item = challege_name
        record=GridLayout(cols=2, size_hint_y=None, height=screen_height * 0.05)
        record_star=Image(source=f"resources/button/star.png", allow_stretch = True,size_hint=(0.35,0.7))
        record_label=Label(
            text=str(self.player_info[f"{challege_name}_score"]),
            size_hint=(0.5, 1),
            color=(0, 0, 0, 1)
        )
        record.add_widget(record_star)
        record.add_widget(record_label)
        button_layout.add_widget(record)
        button_layout.add_widget(enter_button)



        layout.add_widget(item_image)
        layout.add_widget(challege_info)
        layout.add_widget(button_layout)

        return layout

    def on_challege_button_pressed(self, instance):
        """处理按钮点击事件，无论是购买还是使用"""
        item = instance.item
        if not CHALLEGE_OPEN_STATUS[item]:
            self.show_hint(self.language.get_string("challege_is_coming"))
        elif self.player_info["current_level"] < CHALLEGE_LEVEL_LIMIT[item]:
            self.show_hint(self.language.get_string("challege_is_limit").format(CHALLEGE_LEVEL_LIMIT[item]))
        else:
            App.get_running_app().load_challege(item)
            self.dismiss()
            print("enter the challege {}".format(item))

    def show_hint(self, message, duration=3):
        """显示提示文字"""
        hint = HintLabel(message=message, duration=duration)
        hint.show(self)

    # def update_shop_screen(self):
    #     """更新challege界面"""应该不需要这个，因为退出游戏后应该打开打开，打开已经刷新了
    #     print("enter")






class CustomProgressBar(Widget):
    value = NumericProperty(0)
    max_value = NumericProperty(100)
    background_source = StringProperty('background.png')
    progress_source = StringProperty('progress.png')

    def __init__(self, **kwargs):
        super(CustomProgressBar, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, value=self.update_canvas)
        with self.canvas:
            self.bg_rect = Rectangle(source=self.background_source, pos=self.pos, size=self.size)
            self.progress_rect = Rectangle(source=self.progress_source, pos=self.pos, size=(0, self.height))

    def update_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        progress_width = (self.value / float(self.max_value)) * self.width
        self.progress_rect.pos = self.pos
        self.progress_rect.size = (progress_width, self.height)

    def set_target_value(self, target_value, duration=1):
        """平滑地将进度条的值从当前值动画到目标值。

        参数:
        target_value -- 目标进度值，应在 0 和 max_value 之间
        duration -- 动画持续时间（秒），默认为 1 秒
        """
        target_value = max(0, min(target_value, self.max_value))
        anim = Animation(value=target_value, duration=duration)
        anim.start(self)

if __name__ == "__main__":
    GameApp().run()

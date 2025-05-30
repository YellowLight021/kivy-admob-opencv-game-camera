# character.py
from kivy.app import App
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader  # 导入音效加载模块
from config import (CHARACTER_SIZE_FACTOR, GRAVITY_FACTOR, BOUNCE_FACTOR,FRICTION,MIN_VELOCITY_Y_FACTOR,CHARACTER_PUSH_FACTOR,CHARACTER_DAMAGE_WAIT_TIME,
                    BULLET_SPEED_FACTOR,VELOCITY_X_FACTOR,ACCELERATION_FACTOR,BULLET_SIZE_FACTOR,MAX_REVIVE_TIMES,CHARACTER_SPICULATE_FACTOR)
from bullet import Bullet
from healthBar import HealthBar
from status import ShieldStatus
from kivy.core.window import Window
from buff import get_buff_type
class Character(Image):
    def __init__(self,pos,attack=10,heavy_attack=50,health=1000,pow=0,skin="skin_1",name="player1", **kwargs):
        super(Character, self).__init__(**kwargs)
        self.player_info = App.get_running_app().data
        self.source = f"resources/character/{skin}.png"
        self.size_hint = (None, None)
        self.device_window_width, self.device_window_height = Window.size
        self.size = (CHARACTER_SIZE_FACTOR[0] * self.device_window_width, CHARACTER_SIZE_FACTOR[1] * self.device_window_height)
        self.bullet_size=(BULLET_SIZE_FACTOR[0]*self.device_window_width,BULLET_SIZE_FACTOR[0]*self.device_window_height)
        self.pos=pos
        self.allow_stretch = True
        self.velocity_x = 0
        self.velocity_y = 0
        self.min_velocity_y=MIN_VELOCITY_Y_FACTOR*self.device_window_height
        self.forward_x_velocity=VELOCITY_X_FACTOR*self.device_window_width
        self.gravity=GRAVITY_FACTOR*self.device_window_height
        self.acceleration=ACCELERATION_FACTOR*self.device_window_height
        self.bullet_speed=BULLET_SPEED_FACTOR*self.device_window_width
        self.remain_revive_times=MAX_REVIVE_TIMES
        self.name =name
        self.attack=attack
        #如果玩家角色的踩踏伤害，待开发
        self.heavy_attack=heavy_attack
        self.health=health
        self.max_health = health  # 最大血量
        self.pow=pow
        #-1,1 分别对应朝向左、右
        self.forward=1
        #为了稳定性，只能加速一次，所以只设置是否在加速态
        self.is_speed_up=False
        #第二次接触地面后速度回归正常
        self.speed_time= 0
        #控制角色发射子弹的密集度
        self.bullet_cd=CHARACTER_DAMAGE_WAIT_TIME

        #这里处理buff相关，设置一个buff字典，值为buff持续时间
        self.buff_dict={"shield_buff":0,"health_buff":0,"spiculate_buff":0,"push_buff":0}

        # 创建并初始化血条
        self.health_bar = HealthBar(self,health=self.health, max_health=self.max_health)
       # self.health_bar.pos = (self.x + 10, self.y + self.height + 5)  # 血条的位置
        self.add_widget(self.health_bar)  # 将血条添加到怪物
        self.hit_sound = SoundLoader.load("music/jump.wav")

    def revive(self):
        if self.remain_revive_times>0:
            self.health=self.max_health
            self.remain_revive_times=self.remain_revive_times-1
            # #复活后有5秒的护盾保护时间
            self.buff_dict["shield_buff"] = 150
            # if not hasattr(self, "shield_status"):
            #     self.shield_status = ShieldStatus(self, "shield_status")
            #     self.add_widget(self.shield_status)

    def update(self, floors,buffs,coins,bullets,scene_size):
        # 更新怪物的血条
        self.health_bar.update(self.health)

        self.velocity_y = self.gravity+self.velocity_y*(1-FRICTION)

        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y

        self.check_collides_with_buff(new_x,new_y,buffs)
        self.deal_buff_status()
        self.check_collides_with_coin(new_x,new_y,coins)
        collision_floor = self.collides_with_floor(new_x, new_y, floors)
        # collision_with_monster=self.collides_with_monster(new_x, new_y, monsters)
        collision_with_bottom = new_y <= 0
        collision_with_top=new_y>=scene_size[1]
        if collision_floor or collision_with_bottom or collision_with_top:
        # if collision_with_floor or collision_with_bottom or collision_with_top or collision_with_monster:
            self.velocity_y *= BOUNCE_FACTOR
            #每次弹射起身的处理
            if self.velocity_y>0:
                if self.speed_time>0:
                    self.speed_time=self.speed_time-1
                else:
                    self.is_speed_up=False
                    self.velocity_y=self.min_velocity_y
                if self.buff_dict.get("shield_buff")<=0:
                    self.health-=collision_floor.damage
                if(self.bullet_cd==CHARACTER_DAMAGE_WAIT_TIME):
                    bullets.extend(self.generate_bullet())
                    self.bullet_cd=0
                if self.player_info['if_music_on']:
                    self.hit_sound.play()
        #限定其活动的上下界范围
            if collision_with_bottom:
                new_y = 0
            elif collision_with_top:
                new_y=scene_size[1]
            else:
                new_y = max(new_y, self.y)

        self.x = self.clamp(new_x, 0, scene_size[0] - self.width)
        self.y = self.clamp(new_y, 0, scene_size[1] - self.height)

        self.bullet_cd=min(self.bullet_cd+1,CHARACTER_DAMAGE_WAIT_TIME)
        # self.update_health_bar_position()
        #self.health_bar.pos = (self.x + 10, self.y + self.height + 5)

    def collides_with_monster(self, x, y, monsters):
        character_rect = (x, y, self.size[0], self.size[1])
        for monster in monsters:
            monster_rect = (monster.pos[0], monster.pos[1], monster.size[0], monster.size[1])
            if self.rects_collide(character_rect, monster_rect):
                # print("meet monster")
                return True
        return False
    def check_collides_with_buff(self, x, y, buffs):
        character_rect = (x, y, self.size[0], self.size[1])
        for buff in buffs:
            if not buff.touched:
                buff_rect = (buff.pos[0], buff.pos[1], buff.size[0], buff.size[1])
                if self.rects_collide(character_rect, buff_rect):
                    # print("meet monster")
                    buff_type=buff.buff_type
                    for buff_name in self.buff_dict:
                        if(get_buff_type(buff_name)==buff_type):
                            self.buff_dict[buff_name]=0

                    self.buff_dict[buff.name]=buff.times
                    buff.touched=True
                    if buff.name=="shield_buff" and not hasattr(self,"shield_status"):
                        self.shield_status=ShieldStatus(self,buff.name)
                        self.add_widget(self.shield_status)
    def check_collides_with_coin(self, x, y, coins):
        character_rect = (x, y, self.size[0], self.size[1])
        for coin in coins:
            if not coin.touched:
                coin_rect = (coin.pos[0], coin.pos[1], coin.size[0], coin.size[1])
                if self.rects_collide(character_rect, coin_rect):
                    coin.touched=True


    def collides_with_floor(self, x, y, floors):
        character_rect = (x, y, self.size[0], self.size[1])
        for floor in floors:
            # floor_rect = (floor.pos[0], floor.pos[1], floor.size[0], floor.size[1])
            if self.rects_collide(character_rect, floor.inner_rect):
                return floor
        return None
    def collides_with_door(self,door):
        character_rect = (self.pos[0], self.pos[1], self.size[0], self.size[1])
        door_rect = (door.pos[0], door.pos[1], door.size[0], door.size[1])
        if self.rects_collide(character_rect, door_rect):
            return True
        else:
            return False
    def get_damage(self,damage):
        self.health-=damage
    def generate_bullet(self):
        if self.buff_dict['spiculate_buff']>0:
            return [Bullet((self.center_x,(self.pos[1]+self.center_y)/2),self.bullet_size,self.attack*CHARACTER_SPICULATE_FACTOR,
                           (self.bullet_speed*self.forward,0),spiculate=True,owner=self.name,name="bullet_fire.png")]
        elif self.buff_dict['push_buff']>0:
            return [Bullet((self.center_x, (self.pos[1] + self.center_y) / 2), self.bullet_size,
                           self.attack * CHARACTER_PUSH_FACTOR,
                           (self.bullet_speed * self.forward, 0), spiculate=False,push=True, owner=self.name,
                           name="bullet_push.png")]
        else:
            return [Bullet((self.center_x,(self.pos[1]+self.center_y)/2),self.bullet_size,self.attack,
                           (self.bullet_speed*self.forward,0),owner=self.name)]
    def speed_up(self,time):
        # print("start speed :{} isseedup:{}".format(time,self.is_speed_up))
        if not self.is_speed_up:
            self.is_speed_up = True
            self.speed_time=time
            if self.velocity_y < 0:
                self.velocity_y -= self.acceleration
            else:
                #立马往下
                self.velocity_y = -self.velocity_y - self.acceleration

    def move_left(self):
        self.velocity_x = -self.forward_x_velocity
    def move_right(self):
        self.velocity_x = self.forward_x_velocity

    def stop_x_move(self):
        self.velocity_x=0
    def change_forward(self,value):
        if self.forward!=value:
            self.forward = value
            self.flip_image()
    def flip_image(self):
        # 通过改变 uvsize 实现左右翻转
        if self.texture:
            self.texture = self.texture.get_region(0, 0, self.texture.width, self.texture.height)
            self.texture.flip_horizontal()
            # print("flip........................")


    def deal_buff_status(self):
        for buff_name in self.buff_dict.keys():
            if self.buff_dict[buff_name]>=1:
                self.buff_dict[buff_name]=self.buff_dict[buff_name]-1
                if buff_name=="shield_buff" :
                    if self.buff_dict[buff_name]==0 and hasattr(self,"shield_status"):
                        self.remove_widget(self.shield_status)
                        del self.shield_status
                    else:
                        if hasattr(self,"shield_status"):
                            self.shield_status.update()
                if buff_name=="health_buff":
                    self.health=self.max_health



    @staticmethod
    def clamp(value, min_value, max_value):
        return max(min_value, min(value, max_value))

    @staticmethod
    def rects_collide(rect1, rect2):
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2

        return (
            x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2
        )



import os
import random

from kivy.app import App
from kivy.uix.image import Image
from config import GRAVITY_FACTOR,BULLET_SPEED_FACTOR,MONSTER_SPICULATE_FACTOR,MONSTER_DAMAGE_WAIT_TIME,PUSH_FACTOR,MAX_MONSTER_NUM
from bullet import MonsterBullet
from kivy.uix.widget import Widget
from kivy.clock import Clock  # 用于定时更新动画
from healthBar import HealthBar
from kivy.core.window import Window
from kivy.graphics import PushMatrix, PopMatrix, Scale
def generate_challege_1_monster(challege_1_counts,**kwargs):
    if challege_1_counts<100:
        if random.uniform(0,1)>0.6:
            monster_name=random.choice(["littlemonster","smallmonster"])
            return create_monster(monster_name,**kwargs)
        else:
            return None
    elif challege_1_counts<200:
        if random.uniform(0,1)>0.5:
            monster_name=random.choice(["bluemonster","shootmonster","batmonster","littlemonster"])
            return create_monster(monster_name,**kwargs)
        else:
            return None
    elif challege_1_counts<300:
        if random.uniform(0,1)>0.4:
            monster_name=random.choice(["bluemonster","shootmonster","batmonster","fleamonster"])
            return create_monster(monster_name,**kwargs)
        else:
            return None
    elif challege_1_counts<400:
        if random.uniform(0,1)>0.4:
            monster_name=random.choice(["bluemonster","shootmonster","batmonster","fleamonster"])
            return create_monster(monster_name,**kwargs)
        else:
            return None
    else:
        if random.uniform(0,1)>0.3:
            monster_name=random.choice(["bluemonster","shootmonster","batmonster","fleamonster","redbatmonster"])
            return create_monster(monster_name,**kwargs)
        else:
            return None

def generate_challege_2_monster(rank,**kwargs):
    if rank==1:
        monster_name=random.choice(["monster","smallmonster","batmonster"])
        return create_monster(monster_name,**kwargs)
    elif rank==2:
        monster_name=random.choice(["bluemonster","shootmonster","batmonster","ninjamonster","smallzombiemonster"])
        return create_monster(monster_name,**kwargs)
    elif rank==3:
        monster_name=random.choice(["bluemonster","batmonster","fleamonster","smallzombiemonster","redbatmonster",
                                    "ninjamonster","femalezombiemonster","malezombiemonster"])
        return create_monster(monster_name,**kwargs)
    elif rank==4:
        monster_name = random.choice(["bluemonster", "batmonster", "fleamonster","smallzombiemonster","redbatmonster",
                                      "ninjamonster", "femalezombiemonster", "malezombiemonster","flyghostmonster"])
        return create_monster(monster_name, **kwargs)
    else:
        monster_name = random.choice(["bluemonster", "guardmonster", "redbatmonster", "fleamonster", "smallzombiemonster",
                                      "ninjamonster", "femalezombiemonster", "malezombiemonster","eatflowermonster"])
        return create_monster(monster_name, **kwargs)


def create_monster(name,**kwargs):
    # 创建一个名字到类的映射字典
    monster_classes = {
        "batmonster": BatMonster,
        "bluemonster": BlueMonster,
        "littlemonster": LittleMonster,
        "smallmonster": SmallMonster,
        "smallzombiemonster": SmallZombieMonster,
        "monster": Monster,
        "ninjamonster": NinjaMonster,
        "shootmonster": ShootMonster,
        "beemonster": BeeMonster,
        "wallmonster":WallMonster,
        "firemonster":FireMonster,
        "eatflowermonster":EatFlowerMonster,


    }

    # 通过名字从字典中查找类，并实例化
    monster_class = monster_classes.get(name.lower())  # 使用 lower() 忽略大小写
    if monster_class:
        return monster_class(**kwargs)  # 实例化
    else:
        raise ValueError(f"Monster '{name}' does not exist.")


class Monster(Image):
    def __init__(self, pos, attack=25, health=20, point=20, name="monster",with_mirror=False,fps=0.1,keep_forward_count=99999, **kwargs):
        super(Monster, self).__init__(**kwargs)
        self.keep_forward_count=keep_forward_count
        self.forward_count=0
        self.frame_index = 0  # 当前动画帧的索引
        #这里只是为了调size方便，实际其实没有系数
        self.device_window_width, self.device_window_height = (0.75*Window.size[0],0.75*Window.size[1])
        resource_path = f"resources/monster/{name}"
        self.with_mirror=with_mirror
        if with_mirror:
            self.img_num = len(os.listdir(resource_path))//2
            self.animations_mirror=[f"resources/monster/{name}/mirror_{name}_{i}.png" for i in range(1, self.img_num + 1)]
        else:
            self.img_num = len(os.listdir(resource_path))
        self.animations = [f"resources/monster/{name}/{name}_{i}.png" for i in range(1, self.img_num + 1)]
        self.source = self.animations[self.frame_index]  # 初始图像资源
        self.name = name
        # -1,1 分别对应朝向左、右
        self.forward = random.choice([-1,1])
        # self.forward = -1

        self.size_hint = (None, None)
        self.size = (0.0687 * self.device_window_width, 0.05 * self.device_window_height)
        self.allow_stretch=True
        self.velocity_x = self.forward*self.device_window_width * 0.005  # 初始水平速度，用于左右移动
        self.velocity_y = 0  # 垂直速度，用于模拟被动下落
        self.velocity_y_origin=0 # 记录垂直方向速度
        self.bullet_speed = BULLET_SPEED_FACTOR * self.device_window_width
        self.allow_stretch = True
        self.keep_ratio=False
        self.attack = attack
        self.health = health
        self.max_health = health
        self.pos = pos
        self.fps=fps
        self.point = point
        self.gravity=GRAVITY_FACTOR*self.device_window_height  # 定义重力
        self.current_floor = None  # 当前所在的地板，初始化为 None
        # 创建血条并添加到怪物
        self.health_bar = HealthBar(monster=self, health=self.health, max_health=self.max_health)
        self.add_widget(self.health_bar)

        self.damage_wait_time=0



        if random.randint(0,100)<self.point:
            self.drop_coin=True
        else:
            self.drop_coin=False

        #设置一个曲线失败次数越多越容易掉落buff帮助过关，下限站暂定250
        block_times=App.get_running_app().data['block_times']
        random_upper=260+int(140/((block_times+1)**0.75))
        print("random_upper:{}".format(random_upper))
        if random.randint(0,random_upper)<point:
            self.drop_buff=True
        else:
            self.drop_buff=False

    def start_animation(self):
        Clock.schedule_interval(self.update_animation, self.fps)  # 每 0.1 秒更新一帧
    def pause_animation(self):
        # print("pause animation ==============")
        Clock.unschedule(self.update_animation)
    def update(self, floors, bullets, character,monsters, scene_size):
        # 更新位置并检查地板
        self.check_floor(floors)
        self.move(scene_size, character)
        self.check_character(character)
        # 更新怪物的血条
        self.health_bar.update(self.health)



    def update_animation(self, dt):
        self.frame_index = (self.frame_index + 1) % self.img_num
        #print("self.forward:{},self.frame_index:{},self.source:{},self.with_mirror:{}".format(self.forward,self.frame_index,self.source,self.with_mirror))
        if self.with_mirror and self.forward==-1:
            # 切换到下一个帧
            self.source = self.animations_mirror[self.frame_index]  # 更新图像资源

        else:
            self.source = self.animations[self.frame_index]  # 更新图像资源

    def change_forward(self):
        self.velocity_x = -self.velocity_x
        self.forward *= -1  # 切换朝向
        self.forward_count=0
        # self.update_animation(None)
    def move(self, scene_size, character):
        # 先更新水平位置
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.forward_count+=1
        # 检查是否超出游戏场景的左右边界
        scene_left, scene_right, scene_bottom, scene_top = 0, scene_size[0], 0, scene_size[1]
        if (self.x <= scene_left and self.forward<0) or ((self.x+self.width) >= scene_right and self.forward>0):

            self.change_forward()

        # 如果怪物当前不在地板上，施加重力
        if not self.current_floor:
            # print("not current floor vy:{}".format(self.velocity_y))
            self.velocity_y += self.gravity  # 垂直速度受重力影响
        else:
            self.velocity_y = self.velocity_y_origin
            # 约束怪物在当前地板的水平边界内移动
            floor_left, floor_right = self.current_floor.x, self.current_floor.x + self.current_floor.width
            if ((self.center_x <= floor_left and self.forward<0 and self.velocity_y==0) or
                    (self.center_x >= floor_right and self.forward>0 and self.velocity_y==0)):
                # 到达地板边缘则反向水平速度
                self.change_forward()
        if self.keep_forward_count<=self.forward_count:
            self.change_forward()

        # 如果越过左右边界，将怪物位置夹回场景边界内，并反向水平速度
        self.x = max(scene_left, min(self.x, scene_right - self.width))
        # 检查是否超出上下边界
        if self.top >= scene_top:
            # 如果超出顶部边界，将怪物位置夹回顶部边界内，并重置垂直速度
            # self.y = scene_top - self.height
            # self.velocity_y = -self.velocity_y_origin
            pass
        elif self.y <= scene_bottom:
            # 如果超出底部边界，将怪物位置夹回底部边界内，并停止下落
            self.y = scene_bottom
            self.velocity_y = self.velocity_y_origin
    def make_damage(self, character):
        if character.buff_dict.get("shield_buff")<=0:
            character.get_damage(self.attack)
            # character.health -= self.attack
    def get_damage(self,damage):
        self.health-=damage
    def check_character(self, character):
        monster_rect = (self.pos[0], self.pos[1], self.size[0], self.size[1])
        character_rect = (character.pos[0], character.pos[1], character.size[0], character.size[1])
        self.damage_wait_time = (self.damage_wait_time + 1) % MONSTER_DAMAGE_WAIT_TIME
        if self.rects_collide(character_rect, monster_rect) and self.damage_wait_time==0:
            # print("meet monster")

            self.make_damage(character)
            return True

    def check_floor(self, floors):
        # 检测怪物是否站在某个地板上
        floor = self.get_current_floor(floors)

        if floor:
            # 如果找到了新的地板，绑定到该地板并停止下落
            self.current_floor = floor
            self.y = floor.top  # 调整怪物的 y 位置，使其刚好位于地板顶部
            #服务于challege_1关卡
            if floor.must_damage:
                self.health -= floor.damage
                self.drop_coin=False
                self.drop_buff=False
        else:
            # 如果当前没有地板，且怪物的顶部低于当前地板，说明已离开地板
            self.current_floor = None

    def chase_forward(self,character):
        if (self.center_x>character.center_x and self.forward>0) or (self.center_x<character.center_x and self.forward<0):
            self.change_forward()

    def get_current_floor(self, floors):
        # 遍历所有地板，找到怪物当前所在的地板
        for floor in floors:
            if self.collide_floor(floor):
                return floor
        return None

    def generate_monster(self,monsters,monster):
        if len(monsters)<=MAX_MONSTER_NUM:
            monsters.append(monster)
            monster.start_animation()
    def get_health(self,health):
        self.health=min(self.health+health,self.max_health)
    def collide_floor(self, floor):
        # 检查怪物是否与某个地板碰撞（即怪物的底部接触地板的顶部）
        return (self.y <= floor.top <= self.top and
                self.right > floor.x and self.x < floor.right)
    def character_in_search_range(self,character):
        return self.search_range>=((self.center_x-character.center_x)**2+(self.center_y-character.center_y)**2)**0.5
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


        # self.health-=damage
# a jump monster
class LittleMonster(Monster):
    
    def __init__(self, pos, attack=100, health=10, point=20, name="littlemonster", **kwargs):
        super(LittleMonster, self).__init__(pos, attack, health, point, name, **kwargs)
        self.velocity_y_origin=self.device_window_height/50
        self.velocity_x=0
        self.size=(0.06527 * self.device_window_width, 0.05 * self.device_window_height)

class SmallMonster(Monster):
    def __init__(self, pos, attack=15, health=30, point=20, name="smallmonster",with_mirror=True, **kwargs):
        super(SmallMonster, self).__init__(pos, attack, health, point, name,with_mirror, **kwargs)
        self.velocity_y_origin=0
        self.velocity_x=self.forward*self.device_window_width*0.005
        self.size = (0.1486 * self.device_window_width, 0.1 * self.device_window_height)

class BlueMonster(Monster):
    def __init__(self, pos, attack=30, health=40, point=30, name="bluemonster", **kwargs):
        super(BlueMonster, self).__init__(pos, attack, health, point, name, **kwargs)
        self.velocity_y_origin=0
        self.velocity_x=self.forward*self.device_window_width*0.01
        self.size = (0.1527 * self.device_window_width, 0.1 * self.device_window_height)
    #做一个击退效果
    def make_damage(self, character):
        if character.buff_dict.get("shield_buff")<=0:
            character.health -= self.attack
            character.x += self.velocity_x * PUSH_FACTOR*5  # 击退试试可行
class SmallZombieMonster(Monster):
    def __init__(self, pos, attack=20, health=60, point=50, name="smallzombiemonster",with_mirror=True, **kwargs):
        super(SmallZombieMonster, self).__init__(pos, attack, health, point, name,with_mirror, **kwargs)
        self.velocity_y_origin=0
        self.velocity_x=self.forward*self.device_window_width*0.01
        self.size = (0.175 * self.device_window_width, 0.12 * self.device_window_height)
    def make_damage(self,character):
        if character.buff_dict.get("shield_buff") <= 0:
            character.health-=self.attack
            self.health=min(self.attack+self.health,self.max_health)

class NinjaMonster(Monster):
    def __init__(self, pos, attack=50, health=40, point=30, name="ninjamonster",with_mirror=True, **kwargs):
        super(NinjaMonster, self).__init__(pos, attack, health, point, name,with_mirror, **kwargs)
        self.velocity_y_origin=self.device_window_height/50
        self.velocity_x=self.forward*self.device_window_width*0.005
        self.size = (0.172 * self.device_window_width, 0.1 * self.device_window_height)
#射击怪物的基类
class ShootMonster(Monster):
    def __init__(self, pos, attack=20, health=30, point=30, name="shootmonster",with_mirror=True,fps=3, **kwargs):
        super(ShootMonster, self).__init__(pos, attack, health, point, name,with_mirror,fps, **kwargs)
        self.velocity_y_origin=0
        self.velocity_x=0
        self.is_shooted=False
        self.size = (0.12 * self.device_window_width, 0.07 * self.device_window_height)
        # Clock.unschedule(self.update_animation)
        # Clock.schedule_interval(self.update_animation, 3)  # 每 0.1 秒更新一帧

    def update(self,floors,bullets,character,monsters,scene_size):
        # 更新位置并检查地板
        self.bullets=bullets
        self.check_floor(floors)
        # if(self.shoot_wait_count%self.shoot_wait==0):
        #     bullets.extend(self.generate_bullet())
        # self.shoot_wait_count += 1
        if self.frame_index == len(self.animations)-1:
            if not self.is_shooted:
                bullets.extend(self.generate_bullet())
                self.is_shooted=True
        else:
            self.is_shooted=False
        self.move(scene_size,character)
        self.check_character(character)
        # 更新怪物的血条
        self.health_bar.update(self.health)
    def check_character(self, character):
        monster_rect = (self.pos[0], self.pos[1], self.size[0], self.size[1])
        character_rect = (character.pos[0], character.pos[1], character.size[0], character.size[1])
        self.damage_wait_time = (self.damage_wait_time + 1) % MONSTER_DAMAGE_WAIT_TIME
        if self.rects_collide(character_rect, monster_rect) and self.damage_wait_time==0:
            # print("meet monster")

            self.make_damage(character)
            return True
        if self.velocity_x==0:
            self.chase_forward(character)

    def generate_bullet(self):
        return [MonsterBullet(self.center,(self.device_window_width*0.03,self.device_window_width*0.03),self.attack,
                              (self.bullet_speed*self.forward,0),name="monster_bullet.png")]

class EatFlowerMonster(ShootMonster):
    def __init__(self, pos, attack=2, health=60, point=20, name="eatflowermonster",with_mirror=True,fps=1, **kwargs):
        super(EatFlowerMonster, self).__init__(pos, attack, health, point, name,with_mirror,fps, **kwargs)
        self.size = (0.168 * self.device_window_width, 0.1 * self.device_window_height)
    def generate_bullet(self):
        self.get_health(10)
        return [MonsterBullet(self.center,(self.device_window_width*0.07,self.device_window_width*0.07),self.attack,
                              (self.bullet_speed*self.forward,0),name="bullet_green.png",bomb=True)]

class WallMonster(ShootMonster):
    def __init__(self, pos, attack=10, health=60, point=20, name="wallmonster",with_mirror=True,fps=1, **kwargs):
        super(WallMonster, self).__init__(pos, attack, health, point, name,with_mirror,fps, **kwargs)
        self.velocity_x = 0  # 初始水平速度，用于左右移动
        self.size = (0.19 * self.device_window_width, 0.08 * self.device_window_height)
    def generate_bullet(self):
        return []

class FireMonster(ShootMonster):
    def __init__(self, pos, attack=10, health=60, point=30, name="firemonster",with_mirror=True,fps=3, **kwargs):
        super(FireMonster, self).__init__(pos, attack, health, point, name,with_mirror,fps, **kwargs)
        self.velocity_x = 0  # 初始水平速度，用于左右移动
        self.size = (0.18 * self.device_window_width, 0.07 * self.device_window_height)
    def generate_bullet(self):
        return [MonsterBullet((self.center_x,(self.pos[1]*0.7+self.center_y*0.3)),(self.device_window_width*0.7,self.device_window_width*0.15),self.attack,
                              (self.bullet_speed*self.forward*0.02,0),name="bullet_big_fire.png",max_fly_times=10,spiculate=True)]
#飞行怪物的基类
class BatMonster(Monster):
    def __init__(self, pos, attack=20, health=20, point=30, name="batmonster",with_mirror=True,fps=0.1,keep_forward_count=99999, **kwargs):
        super(BatMonster, self).__init__(pos, attack, health, point, name,with_mirror,fps,keep_forward_count, **kwargs)
        self.velocity_x = self.forward*self.device_window_width*0.005
        self.velocity_y = self.device_window_height*0.005
        self.size = (0.10625 * self.device_window_width, 0.05 * self.device_window_height)
        self.search_range=self.device_window_width*1 # 怪物追踪范围

    def move(self,scene_size,character):
        #新增设定自由活动的怪物
        if self.keep_forward_count!=99999:
            self.x += self.velocity_x
            self.forward_count+=1
            if self.keep_forward_count<=self.forward_count:
                self.change_forward()
        # 先判断是否在搜索范围
        if self.character_in_search_range(character):
            if (character.center_x<self.center_x and self.forward>0) or (character.center_x>self.center_x and self.forward<0):
                self.change_forward()
            self.x += self.velocity_x
            self.y += self.velocity_y*(1 if character.center_y>self.center_y else -1)

        # 检查是否超出游戏场景的左右边界
        scene_left, scene_right, scene_bottom, scene_top = 0, scene_size[0], 0, scene_size[1]

        self.x = max(scene_left, min(self.x, scene_right - self.width))
        self.y=max(scene_bottom,min(self.y,scene_top-self.height))





class BeeMonster(BatMonster):
    def __init__(self, pos, attack=15, health=30, point=30, name="beemonster",with_mirror=True,fps=0.3,keep_forward_count=75, **kwargs):
        super(BeeMonster, self).__init__(pos, attack, health, point, name,with_mirror,fps,keep_forward_count, **kwargs)
        self.velocity_x = self.forward*self.device_window_width*0.005
        self.velocity_y = 0
        self.size = (0.16 * self.device_window_width, 0.07 * self.device_window_height)
        self.search_range=0 # 怪物追踪范围
        self.is_shooted = False
    def update(self, floors, bullets, character,monsters, scene_size):
        # 更新位置并检查地板
        self.bullets = bullets
        if self.frame_index == len(self.animations) - 1:
            if not self.is_shooted:
                bullets.extend(self.generate_bullet())
                # print("bee shoot")
                self.is_shooted = True
        else:
            self.is_shooted = False
        self.move(scene_size, character)
        self.check_character(character)
        # 更新怪物的血条
        self.health_bar.update(self.health)
    def generate_bullet(self):
        return [MonsterBullet(self.center,(self.device_window_width*0.035,self.device_window_width*0.035),self.attack,
                              (0,-self.bullet_speed),name="down_bullet.png")]











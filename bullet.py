# bullet.py
from kivy.app import App
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader  # 导入音效加载模块
from kivy.core.window import Window
from config import MONSTER_BULLET_FACTOR,BULLET_PUSH_FACTOR,MONSTER_SPICULATE_FACTOR

class Bullet(Image):
    def __init__(self, pos,size,damage,speed,spiculate=False,push=False,bomb=False,owner="character",name="bullet.png",
                 max_fly_times=144,**kwargs):
        super(Bullet, self).__init__(**kwargs)
        self.device_window_width, self.device_window_height = Window.size
        self.source = f"resources/bullet/{name}"
        self.size_hint = (None, None)
        self.size = size  # 子弹大小
        self.allow_stretch = True
        self.pos = [pos[0]-(speed[0]<0)*size[0],pos[1]]
        self.spiculate=spiculate
        self.push=push
        self.bomb=bomb
        self.damage = damage
        self.velocity_x,self.velocity_y = speed
        self.speed=(self.velocity_x**2+self.velocity_y**2)**0.5
        self.owner=owner
        self.player_info = App.get_running_app().data
        self.hit_sound = SoundLoader.load("music/bullet_hit.wav")  # 替换为实际的音效路径
        #记录飞行时间飞行结束后自动消失
        self.max_fly_times=max_fly_times
        #子弹朝向的问题
        if self.velocity_x<0 and self.texture:
            self.texture = self.texture.get_region(0, 0, self.texture.width, self.texture.height)
            self.texture.flip_horizontal()

        # print("bullet name {} bullet size{}".format(name, self.size))
    def update(self,monsters,floors,scene_size,bullets):
        #这里返回false是指是否删除掉
        self.x += self.velocity_x  # 向右移动
        self.y += self.velocity_y
        self.max_fly_times=self.max_fly_times-1
        if (self.check_collision(monsters) or self.check_collision(floors)):
            if self.player_info['if_music_on']:
                self.play_hit_sound()  # 播放命中音效
            if self.bomb:
                bullets.extend(self.generate_bullet())

            return False
        elif (self.max_fly_times<=0 or self.x>scene_size[0] or self.x<0 or self.y>scene_size[1] or self.y<0):
            return False
        else:
            return True

    def generate_bullet(self):
        return [Bullet(self.center,(self.device_window_width*0.02,self.device_window_width*0.02),self.damage,
                              (self.speed,self.speed),name="bullet_green.png",spiculate=True,max_fly_times=16),
                Bullet(self.center, (self.device_window_width*0.02,self.device_window_width*0.02), self.damage,
                       (-self.speed, self.speed), name="bullet_green.png",spiculate=True,max_fly_times=16),
                Bullet(self.center, (self.device_window_width*0.02,self.device_window_width*0.02), self.damage,
                       (self.speed,-self.speed), name="bullet_green.png",spiculate=True,max_fly_times=16),
                Bullet(self.center, (self.device_window_width*0.02,self.device_window_width*0.02), self.damage,
                       (-self.speed,-self.speed), name="bullet_green.png",spiculate=True,max_fly_times=16)
                ]
    def check_collision(self, entitys):
        for entity in entitys:
            if self.rects_collide((self.x, self.y, self.width, self.height),
                                  (entity.x, entity.y, entity.width, entity.height)):
                if hasattr(entity, "health"):
                    if (not hasattr(entity, "buff_dict")) or entity.buff_dict.get("shield_buff",0)<=0:
                        #todo bullet_damage
                        entity.get_damage(self.damage)
                        #entity.health -= self.damage  # 受到伤害
                        entity.x+=self.velocity_x*self.push*BULLET_PUSH_FACTOR#击退试试可行
                        # entity.x += self.velocity_x * 1 * BULLET_PUSH_FACTOR
                if not self.spiculate:
                    return True
        return False
    def play_hit_sound(self):
        if self.hit_sound:
            self.hit_sound.play()
        else:
            print("音效未加载成功，无法播放")

    def cleanup(self):
        """在 Bullet 被销毁时调用，停止音效"""
        if self.hit_sound:
            self.hit_sound.stop()
            self.hit_sound.unload()  # 释放资源
            self.hit_sound = None  # 防止重复调用时出错

    def on_remove(self):
        """当 Bullet 被移除时清理资源"""
        self.cleanup()
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

class MonsterBullet(Bullet):
    def __init__(self, pos,size, damage, speed,spiculate=False,push=False,bomb=False, owner="monster",name="monster_bullet",max_fly_times=144, **kwargs):
        super(MonsterBullet, self).__init__(pos,size, damage*MONSTER_BULLET_FACTOR, speed,spiculate,push,bomb, owner,name,max_fly_times, **kwargs)
        self.hit_sound=None
        self.allow_stretch=True
        self.keep_ratio=False
    def update(self,character,floors,scene_size,bullets):
        self.x += self.velocity_x  # 向右移动
        self.y += self.velocity_y
        self.max_fly_times = self.max_fly_times - 1
        if (self.max_fly_times<=0 or self.check_collision(character) or self.check_collision(floors)
                or self.x>scene_size[0] or self.x<0 or self.y>scene_size[1] or self.y<0):
            if self.bomb:
                bullets.extend(self.generate_bullet())
            return False
        else:
            return True

    def generate_bullet(self):
        return [MonsterBullet(self.center,(self.device_window_width*0.02,self.device_window_width*0.02),self.damage*0.5*MONSTER_SPICULATE_FACTOR,
                              (self.speed,self.speed),name="bullet_green.png",spiculate=True,max_fly_times=16),
                MonsterBullet(self.center, (self.device_window_width*0.02,self.device_window_width*0.02), self.damage*0.5*MONSTER_SPICULATE_FACTOR,
                       (-self.speed, self.speed), name="bullet_green.png",spiculate=True,max_fly_times=16),
                MonsterBullet(self.center, (self.device_window_width*0.02,self.device_window_width*0.02), self.damage*0.5*MONSTER_SPICULATE_FACTOR,
                       (self.speed,-self.speed), name="bullet_green.png",spiculate=True,max_fly_times=16),
                MonsterBullet(self.center, (self.device_window_width*0.02,self.device_window_width*0.02), self.damage*0.5*MONSTER_SPICULATE_FACTOR,
                       (-self.speed,-self.speed), name="bullet_green.png",spiculate=True,max_fly_times=16)
                ]
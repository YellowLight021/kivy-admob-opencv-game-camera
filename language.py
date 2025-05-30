class LangManager:
    def __init__(self,lang_index):

        self.lang_dict={}
        cn_dict={
            "retraction":"颈部后仰(跳跃加速)",
            "tilt":"颈部拉升(左右移动)",
            "rotation": "颈部旋转(改变朝向)",
            "record":"运动记录:",
            "count":"次数：{}",
            "switch camera":"切换到摄像头{}",
            "only one":"你只有一个摄像头",
            "face loss":"未检测到人脸",
            "need money":"金币不够",
            "play level":"第{}关",
            "ad reward tip":"看广告可额外领取{}金币",
            "share reward tip": "分享可额外领取{}金币",
            "pve info":"第{}关",
            "back":"返回",
            "revive":"复活",
            "revive_tip":"还剩下{}次复活机会，是否看广告复活",
            "camera open":"摄像头未打开",
            "continue":"继续",
            "more coin": "更多金币",
            "camera tilt":"正对摄像头，颈部侧倾",
            "camera rotate":"正对摄像头，颈部旋转",
            "camera retraction":"正对摄像头，颈部后仰",
            "buy":"购买",
            "choose":"选择",
            "restart tip":"部分设备需要打开摄像头后重新进入游戏",
            "keep left":"持续拉升,向左移动",
            "keep right": "持续拉升,向右移动",
            "move_left_right": "学会左右移动",
            "forward_left_right": "学会左右看",
            "start_big_jump": "学会大跳",
            "up not unlocked": "大跳功能尚未开启",
            "shake not unlocked": "左右移动功能尚未开启",
            "turn not unlocked": "切换朝向功能尚未开启",
            "boss speak 1":"我在第100关等你",
            "boss speak 2": "放过你的脖子,你确定吗？",
            "boss speak 3": "天才是见我的起码要求",
            "boss speak 4": "小可爱,放弃吧",
            "boss speak 5": "不要低着头玩手机啦,小子",
            "boss speak 6": "在晃动你的脑子的时候,注意动作标准哟！",
            "boss speak 7": "大跳需要技巧，不是所有人能够随便掌握的",
            "boss speak 8": "很多人在见我的路上就倒下了,包括你吗？",
            "boss speak 9": "点击我头上的动作图标试试,你看到了什么",
            "boss speak 10": "没有人能打败我,包括你",
            "start":"开始",
            "challege_1":"绝境攀升",
            "challege_2":"末日狂袭",
            "challege_is_coming":"敬请期待",
            "challege_is_limit":"通关{}解锁"


        }
        en_dict={
            "retraction":"Neck Tilt Back",
            "tilt":"Side Neck Stretch",
            "rotation": "Neck Rotation",
            "record":"Record:",
            "count":"times：{}",
            "switch camera":"switch camera to {}",
            "only one": "on other camera",
            "face loss":"no face detected",
            "need money":"coin is not enough ",
            "play level":"lv {}",
            "ad reward tip":"watch the AD to get {} coin",
            "share reward tip": "share to get {} coin",
            "pve info": "level {}",
            "back": "return",
            "revive": "revive",
            "revive_tip": "{} revive remained, watch ad",
            "camera open": "camera not opened",
            "continue": "continue",
            "more coin": "more money",
            "camera tilt": "face your camera and tilt neck",
            "camera rotate": "face your camera and rotate neck",
            "camera retraction": "face your camera and tilt back neck",
            "buy": "buy",
            "choose": "choose",
            "restart tip": "please re-enter the game",
            "keep left": "keep tilting head move to left",
            "keep right": "keep tilting head move to right",
            "move_left_right": "study to move",
            "forward_left_right": "study to change forward",
            "start_big_jump": "study a big jump",
            "up not unlocked":"big jump is not unlocked yet",
            "shake not unlocked": "movement is not unlocked yet",
            "turn not unlocked": "forward change is not unlocked yet",
            "boss speak 1": "I'm waiting for you at level 100",
            "boss speak 2": "Let go of your neck, are you sure?",
            "boss speak 3": "Only genius have chance to meet me",
            "boss speak 4": "Little cutie, give up",
            "boss speak 5": "Don't play on your phone with your head down, kid",
            "boss speak 6": "While shaking your brain, keep face in camera!",
            "boss speak 7": "Big jumps require skill!",
            "boss speak 8": "Will you also fail on the road to meeting me?",
            "boss speak 9": "Click the action icon above my head and see what you notice",
            "boss speak 10": "No one can beat me, not even you",
            "start": "start",
            "challege_1": "Leap of Fate",
            "challege_2": "Endless monsters",
            "challege_is_coming": "Coming Soon",
            "challege_is_limit": "unlock at lv{}"

        }
        self.lang_dict["en"]=en_dict
        self.lang_dict["zh"]=cn_dict
        self.lang_index=int(lang_index)
        self.lan_list = ["en", "zh"]
        self.current_lan=self.lan_list[self.lang_index]
    def switch_lan(self):

        self.lang_index=(self.lang_index+1)%2
        self.current_lan=self.lan_list[self.lang_index]
        return self.lang_index
    def get_string(self,key):
        # print('::::::::{}{}'.format(key,self.current_lan))
        if key not in self.lang_dict[self.current_lan]:
            return key
        return self.lang_dict[self.current_lan][key]

    def get_lan(self):
        return self.lan_list[(self.lang_index+1)%2]


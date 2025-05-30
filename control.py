# control.py
from config import SPEED_UP_TIME,GUIDE_LEVELS

class Controler:
    def __init__(self):
        self.geture_id=0
    def on_key_down(self,character, key):
        if key == 276:  # 左键
            character.change_forward(1)
        elif key == 275:  # 右键
            character.change_forward(0)
    def on_key_up(self,character, key):
        if key in (276, 275):  # 左或右键
            character.velocity_x = 0  # 停止水平移动

    def on_gesture(self,character,gesture_list):
        '''定义姿势：0不确定,同检测不到人脸一样处理1仰视、2歪左、3歪右、4左向、5右向、6低头、7正视'''
        geture_id=gesture_list[0]
        if geture_id==1 and character.player_info.get("retraction_opened",False):
            character.speed_up(SPEED_UP_TIME)
        elif geture_id==2 and character.player_info.get("tilt_opened",False):
            character.move_left()
        elif geture_id==3 and character.player_info.get("tilt_opened",False):
            character.move_right()
        elif geture_id==7:
            character.stop_x_move()
        elif geture_id==4 and character.player_info.get("rotation_opened",False):
            character.change_forward(-1)
        elif geture_id==5 and character.player_info.get("rotation_opened",False):
            character.change_forward(1)
    # def on_gesture(self,character,gesture_list):
    #     '''定义姿势：0不确定,同检测不到人脸一样处理1仰视、2歪左、3歪右、4左向、5右向、6低头、7正视'''
    #     geture_id=gesture_list[0]
    #     if geture_id==1:
    #         if character.velocity_y<0:
    #             character.velocity_y-=ACCELERATION
    #         else:
    #             character.velocity_y = -character.velocity_y -ACCELERATION
    #     elif geture_id==2:
    #         character.velocity_x = -VELOCITY_X
    #     elif geture_id==3:
    #         character.velocity_x = VELOCITY_X
    #     # elif geture_id==6:
    #     #     character.velocity_y -= ACCELERATION
    #     elif geture_id==7:
    #         character.velocity_x = 0
    #     elif geture_id==4:
    #         print("change forward")
    #         character.change_forward(0)
    #     elif geture_id==5:
    #         character.change_forward(1)
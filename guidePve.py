
from kivy.uix.image import Image

from pve import PVE

from kivy.properties import ListProperty


class GUIDE_PVE(PVE):
    #目前同一个时刻只支持一个动作默认姿态是互斥的，但是后续可能会扩展所以先这么干申请list类型
    gesture = ListProperty([0, 0])
    #level表示第几个关卡
    def __init__(self,player_info,detector, **kwargs):
        super(GUIDE_PVE, self).__init__(player_info,detector,**kwargs)


    def create_face_image(self):
        # print("hhh======{}={}============".format(self.device_window_width, self.device_window_height))
        face_image=Image(size_hint=(0.3, 0.18),pos_hint={"center_x": 0.5, "center_y": 0.64},keep_ratio=False,allow_stretch=True )
        return face_image



import xml.etree.ElementTree as ET
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
import random
from character import Character
from monster import create_monster
from buff import create_buff
from coin import create_coin
from floor import create_floor,Floor
from door import Door
from kivy.core.window import Window


def read_xml_info(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    size_info = {}
    ground_info = []
    monster_info = []
    window_info=[]
    character_info = []
    door_info=[]
    buff_info=[]
    coin_info=[]

    # 读取size信息
    size_elem = root.find('size')
    size_info['width'] = int(size_elem.find('width').text)
    size_info['height'] = int(size_elem.find('height').text)

    # 读取ground和monster的信息
    for object_elem in root.findall('object'):
        name = object_elem.find('name').text
        bndbox_elem = object_elem.find('bndbox')
        bndbox_info = {
            'xmin': int(bndbox_elem.find('xmin').text),
            'ymin': int(bndbox_elem.find('ymin').text),
            'xmax': int(bndbox_elem.find('xmax').text),
            'ymax': int(bndbox_elem.find('ymax').text)
        }

        if 'ground' in name:
            bndbox_info["ground_name"] = name
            ground_info.append(bndbox_info)
        elif 'monster' in name:
            bndbox_info["monster_name"]=name
            monster_info.append(bndbox_info)
        elif name=='window':
            window_info.append(bndbox_info)
        elif name=='character':
            character_info.append(bndbox_info)
        elif name=="door":
            door_info.append(bndbox_info)
        elif 'buff' in name:
            bndbox_info["buff_name"] = name
            buff_info.append(bndbox_info)
        elif 'coin' in name:
            bndbox_info['coin_name']=name
            coin_info.append(bndbox_info)

    return size_info, ground_info, monster_info,window_info,character_info,door_info,buff_info,coin_info

def generate_scene_info(xml_file_path):
    device_window_width, device_window_height = Window.size
    print("start generate scene , device size is {}".format((device_window_width,device_window_height)))
    size_info, ground_info, monster_info,window_info,character_info,door_info,buff_info,coin_info = read_xml_info(xml_file_path)
    scene_inf={}
    scene_width=size_info['width']
    scene_height = size_info['height']
    window_width=window_info[0]["xmax"]-window_info[0]["xmin"]
    window_height = window_info[0]["ymax"] - window_info[0]["ymin"]
    #以窗口尺寸为基本单位1
    #场景尺寸信息
    scene_inf["scene_width"]=scene_width/window_width*device_window_width
    scene_inf["scene_height"] = scene_height / window_height*device_window_height
    #角色进入游戏的初始位置信息
    scene_inf["both_pos"] = []

    ########
    '''
    这里位置计算都是大场景尺寸*相对比值获得
    '''
    ########
    for character in character_info:
        pos_x=scene_inf["scene_width"]*character["xmin"]/scene_width
        #这里注意标注工具与kivy坐标的y是相反的
        pos_y=scene_inf["scene_height"]*(1-character["ymax"]/scene_height)
        scene_inf["both_pos"].append((pos_x,pos_y))
    scene_inf["monster_pos"] = []
    for monster in monster_info:
        pos_x =  scene_inf["scene_width"]*monster["xmin"] / scene_width
        pos_y = scene_inf["scene_height"]*(1-monster["ymax"]/scene_height)
        scene_inf["monster_pos"].append((pos_x, pos_y,monster['monster_name']))

    scene_inf["door_pos"] = []
    for door in door_info:
        pos_x =  scene_inf["scene_width"]*door["xmin"] / scene_width
        pos_y = scene_inf["scene_height"]*(1-door["ymax"]/scene_height)
        scene_inf["door_pos"].append((pos_x, pos_y))

    scene_inf["floor_pos"] = []
    ##########
    for floor in ground_info:
        pos_x=scene_inf["scene_width"]*floor['xmin']/scene_width
        pos_y=scene_inf["scene_height"]*(1-floor["ymax"]/scene_height)
        width=scene_inf["scene_width"]*(floor['xmax']-floor['xmin'])/scene_width
        height=scene_inf["scene_height"]*(floor['ymax']-floor['ymin'])/scene_height
        scene_inf["floor_pos"].append((pos_x,pos_y,width,height,floor['ground_name']))

    scene_inf["buff_pos"] = []
    for buff in buff_info:
        pos_x =  scene_inf["scene_width"]*buff["xmin"] / scene_width
        pos_y = scene_inf["scene_height"]*(1-buff["ymax"]/scene_height)
        scene_inf["buff_pos"].append((pos_x, pos_y,buff['buff_name']))

    scene_inf["coin_pos"] = []
    for coin in coin_info:
        pos_x =  scene_inf["scene_width"]*coin["xmin"] / scene_width
        pos_y = scene_inf["scene_height"]*(1-coin["ymax"]/scene_height)
        scene_inf["coin_pos"].append((pos_x, pos_y,coin['coin_name']))

    return scene_inf

def generate_scene(monster_list,floor_list,buff_list,coin_list,player_info):
    #为了配置方便，这里将关卡id映射出对应的bg_id以及对应的level的具体位置
    current_level=player_info['challenge_level']
    bg_num_id=current_level%10
    one_place_id=current_level//10
    xml_file_path = f"resources/level/{one_place_id}/scene_{bg_num_id}.xml"
    scene_inf=generate_scene_info(xml_file_path)
    scene_w,scene_h=scene_inf["scene_width"],scene_inf["scene_height"]
    layout = FloatLayout(size_hint=(None, None),size=(scene_w, scene_h))
    # background = Image(source=f"resources/background/scene_{bg_num_id}.png", size_hint=(1, 1), allow_stretch=True,
    #                    keep_ratio=False)
    background = Image(source=f"resources/background/scene_{bg_num_id}.png",pos=(0,0), size=(scene_w, scene_h), allow_stretch=True,
                       keep_ratio=False)
    layout.add_widget(background)

    #支持随机一个出生点
    character_pos=random.choice(scene_inf["both_pos"])
    character=Character(character_pos,skin=player_info['current_skin'])



    door_pos = random.choice(scene_inf["door_pos"])
    print("========door pos :{},scene{}====".format(door_pos,(scene_w,scene_h)))
    door = Door(door_pos)
    layout.add_widget(door)


    for floor in scene_inf['floor_pos']:
        # new_floor=Floor(floor[4],floor[:2],floor[2:4])
        new_floor=create_floor(floor[4],pos=floor[:2],size=floor[2:4])
        layout.add_widget(new_floor)
        floor_list.append(new_floor)
    layout.add_widget(character)
    for monster in scene_inf['monster_pos']:
        # new_monster=MonsterZombie(monster[:2])
        new_monster=create_monster(monster[2],pos=monster[:2])
        layout.add_widget(new_monster)

        monster_list.append(new_monster)
    for buff in scene_inf['buff_pos']:
        new_buff=create_buff(buff[2],pos=buff[:2])
        buff_list.append(new_buff)
        layout.add_widget(new_buff)

    for coin in scene_inf['coin_pos']:
        new_coin=create_coin(coin[2],pos=coin[:2])
        coin_list.append(new_coin)
        layout.add_widget(new_coin)
    return layout,character,scene_w,scene_h,door

def generate_guide_scene(monster_list,floor_list,buff_list,coin_list,player_info):
    #为了配置方便，这里将关卡id映射出对应的bg_id以及对应的level的具体位置
    current_level=player_info['challenge_level']

    xml_file_path = f"resources/level/0/scene_{current_level}.xml"
    scene_inf=generate_scene_info(xml_file_path)
    scene_w,scene_h=scene_inf["scene_width"],scene_inf["scene_height"]
    layout = FloatLayout(size_hint=(None, None),size=(scene_w, scene_h))
    # background = Image(source=f"resources/background/scene_{bg_num_id}.png", size_hint=(1, 1), allow_stretch=True,
    #                    keep_ratio=False)
    background = Image(source=f"resources/background/scene_{current_level}.png",pos=(0,0), size=(scene_w, scene_h), allow_stretch=True,
                       keep_ratio=False)
    layout.add_widget(background)

    #支持随机一个出生点
    character_pos=random.choice(scene_inf["both_pos"])
    character=Character(character_pos,skin=player_info['current_skin'])
    layout.add_widget(character)

    #支持随机一个出口点
    door_pos = random.choice(scene_inf["door_pos"])
    print("========door pos :{},scene{}====".format(door_pos,(scene_w,scene_h)))
    door = Door(door_pos)
    layout.add_widget(door)

    for floor in scene_inf['floor_pos']:
        # new_floor=Floor(floor[4],floor[:2],floor[2:4])
        new_floor=create_floor(floor[4],pos=floor[:2],size=floor[2:4])
        layout.add_widget(new_floor)
        floor_list.append(new_floor)
    for monster in scene_inf['monster_pos']:
        # new_monster=MonsterZombie(monster[:2])
        new_monster=create_monster(monster[2],pos=monster[:2])
        layout.add_widget(new_monster)

        monster_list.append(new_monster)
    for buff in scene_inf['buff_pos']:
        new_buff=create_buff(buff[2],pos=buff[:2])
        buff_list.append(new_buff)
        layout.add_widget(new_buff)

    for coin in scene_inf['coin_pos']:
        new_coin=create_coin(coin[2],pos=coin[:2])
        coin_list.append(new_coin)
        layout.add_widget(new_coin)
    return layout,character,scene_w,scene_h,door

def generate_challege_1_scene(monster_list,floor_list,buff_list,coin_list,player_info):

    xml_file_path = f"resources/level/challege_1/challege_1.xml"
    scene_inf=generate_scene_info(xml_file_path)
    scene_w,scene_h=scene_inf["scene_width"],scene_inf["scene_height"]
    layout = FloatLayout(size_hint=(None, None),size=(scene_w, scene_h))
    # background = Image(source=f"resources/background/scene_{bg_num_id}.png", size_hint=(1, 1), allow_stretch=True,
    #                    keep_ratio=False)
    background = Image(source=f"resources/background/challege_1.png",pos=(0,0), size=(scene_w, scene_h), allow_stretch=True,
                       keep_ratio=False)
    layout.add_widget(background)

    #支持随机一个出生点
    character_pos=random.choice(scene_inf["both_pos"])
    character=Character(character_pos,skin=player_info['current_skin'])

    for floor in scene_inf['floor_pos']:
        # new_floor=Floor(floor[4],floor[:2],floor[2:4])
        new_floor=create_floor(floor[4],pos=floor[:2],size=floor[2:4])
        layout.add_widget(new_floor)
        floor_list.append(new_floor)
    layout.add_widget(character)
    for monster in scene_inf['monster_pos']:
        # new_monster=MonsterZombie(monster[:2])
        new_monster=create_monster(monster[2],pos=monster[:2])
        layout.add_widget(new_monster)

        monster_list.append(new_monster)
    for buff in scene_inf['buff_pos']:
        new_buff=create_buff(buff[2],pos=buff[:2])
        buff_list.append(new_buff)
        layout.add_widget(new_buff)

    for coin in scene_inf['coin_pos']:
        new_coin=create_coin(coin[2],pos=coin[:2])
        coin_list.append(new_coin)
        layout.add_widget(new_coin)
    return layout,character,scene_w,scene_h

def generate_challege_2_scene(monster_list,floor_list,buff_list,coin_list,player_info):

    xml_file_path = f"resources/level/challege_2/challege_2_1.xml"
    scene_inf=generate_scene_info(xml_file_path)
    scene_w,scene_h=scene_inf["scene_width"],scene_inf["scene_height"]
    layout = FloatLayout(size_hint=(None, None),size=(scene_w, scene_h))
    # background = Image(source=f"resources/background/scene_{bg_num_id}.png", size_hint=(1, 1), allow_stretch=True,
    #                    keep_ratio=False)
    background = Image(source=f"resources/background/challege_2_1.png",pos=(0,0), size=(scene_w, scene_h), allow_stretch=True,
                       keep_ratio=False)
    layout.add_widget(background)

    #支持随机一个出生点
    character_pos=random.choice(scene_inf["both_pos"])
    character=Character(character_pos,skin=player_info['current_skin'])

    for floor in scene_inf['floor_pos']:
        # new_floor=Floor(floor[4],floor[:2],floor[2:4])
        new_floor=create_floor(floor[4],pos=floor[:2],size=floor[2:4])
        layout.add_widget(new_floor)
        floor_list.append(new_floor)
    layout.add_widget(character)
    for monster in scene_inf['monster_pos']:
        # new_monster=MonsterZombie(monster[:2])
        new_monster=create_monster(monster[2],pos=monster[:2])
        layout.add_widget(new_monster)

        monster_list.append(new_monster)
    for buff in scene_inf['buff_pos']:
        new_buff=create_buff(buff[2],pos=buff[:2])
        buff_list.append(new_buff)
        layout.add_widget(new_buff)

    for coin in scene_inf['coin_pos']:
        new_coin=create_coin(coin[2],pos=coin[:2])
        coin_list.append(new_coin)
        layout.add_widget(new_coin)
    return layout,character,scene_w,scene_h




if __name__=="__main__":
    xml_file_path = r"resources/level/scene_1.xml"  # 替换为实际的XML文件路径
    # size_info, ground_info, monster_info,window_info,character_info  = read_xml_info(xml_file_path)
    print(generate_scene_info(xml_file_path))
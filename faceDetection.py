import os

# import tensorflow as tf
from typing import List, Tuple
import cv2
from faceModel.nms import non_maximum_suppression
from faceModel.tfTypes import Detection,RectOrOval,Annotation,Point,Colors,Line
from model import TensorFlowModel
import numpy as np
from config import RAW_SCORE_LIMIT,MIN_SCORE,MIN_SUPPRESSION_THRESHOLD
import time


class FaceDetection:
    '''LEFT_EYE = 0
    RIGHT_EYE = 1
    NOSE_TIP = 2
    MOUTH = 3
    LEFT_EYE_TRAGION = 4
    RIGHT_EYE_TRAGION = 5'''

    @staticmethod
    def getsture_recognize(face_pos):


        '''定义姿势：
        0不确定,同检测不到人脸一样处理
        1仰视
        2歪左
        3歪右
        4左向
        5右向
        6低头
        7正视'''
        # print("face_pos:{}".format(face_pos))
        # import pdb
        # pdb.set_trace()
        if not face_pos or ("2" not in face_pos):
            return 0
        left_eye_pos=face_pos["0"]
        right_eye_pos = face_pos["1"]
        nose_tip_pos = face_pos["2"]
        mouth_pos = face_pos["3"]
        left_eye_tragion_pos = face_pos["4"]
        right_eye_tragion_pos = face_pos["5"]
        '''这里注意cv2的坐标原点在左上角位置，而kivy坐标原点在左下角位置'''
        #判断仰视2纵坐标同时高于所有纵坐标
        if nose_tip_pos[1]<left_eye_tragion_pos[1] and nose_tip_pos[1]<right_eye_tragion_pos[1]:
            # print("{},{},{},{}".format(nose_tip_pos[1],left_eye_pos[1],nose_tip_pos[1],right_eye_pos[1]))
            return 1

        #正视0高于4,1高于5，鼻子在0,1横坐标之间
        if left_eye_pos[1] < left_eye_tragion_pos[1] and right_eye_pos[1] < right_eye_tragion_pos[1] \
                and nose_tip_pos[0]>left_eye_pos[0] and nose_tip_pos[0]<right_eye_pos[0]:
            return 7
        # 判断低头0,1纵坐标都是小于4,5的纵坐标
        # if left_eye_pos[1] > left_eye_tragion_pos[1] :
        #     return 6
        #向左2横坐标小于0横坐标
        # if left_eye_pos[0]<=left_eye_tragion_pos[0] or nose_tip_pos[0]<=left_eye_tragion_pos[0]:
        if nose_tip_pos[0]<left_eye_tragion_pos[0]:
            return 4

        #向右2横坐标大于1横坐标
        # if right_eye_pos[0] >= right_eye_tragion_pos[0] or nose_tip_pos[0]>=right_eye_tragion_pos[0]:
        if nose_tip_pos[0]>right_eye_tragion_pos[0]:
            return 5
            # 歪左4,0,1,5升左，降右
            # 左移

        if left_eye_tragion_pos[1] >= right_eye_pos[1]:
            # if left_eye_tragion_pos[1]>=left_eye_pos[1] and left_eye_pos[1]>right_eye_pos[1] \
            #     and right_eye_pos[1]>right_eye_tragion_pos[1]:
            # if right_eye_tragion_pos[1] >= nose_tip_pos[1]:
            return 2
        # if left_eye_tragion_pos[1]<left_eye_pos[1] and left_eye_pos[1]<right_eye_pos[1] \
        #     and right_eye_pos[1]<=right_eye_tragion_pos[1]:
        if right_eye_tragion_pos[1] >= left_eye_pos[1]:
            # if left_eye_tragion_pos[1] <= nose_tip_pos[1] :
            return 3





        return 0




    def _decode_boxes(self, raw_boxes: np.ndarray) -> np.ndarray:
        """Simplified version of
        mediapipe/calculators/tflite/tflite_tensors_to_detections_calculator.cc
        """
        # width == height so scale is the same across the board
        scale = self.input_shape[1]
        num_points = raw_boxes.shape[-1] // 2
        # scale all values (applies to positions, width, and height alike)
        boxes = raw_boxes.reshape(-1, num_points, 2) / scale
        # adjust center coordinates and key points to anchor positions
        boxes[:, 0] += self.anchors
        for i in range(2, num_points):
            boxes[:, i] += self.anchors
        # convert x_center, y_center, w, h to xmin, ymin, xmax, ymax
        center = np.array(boxes[:, 0])
        half_size = boxes[:, 1] / 2
        boxes[:, 0] = center - half_size
        boxes[:, 1] = center + half_size
        return boxes

    def _get_sigmoid_scores(self, raw_scores: np.ndarray) -> np.ndarray:
        """Extracted loop from ProcessCPU (line 327) in
        mediapipe/calculators/tflite/tflite_tensors_to_detections_calculator.cc
        """
        # just a single class ("face"), which simplifies this a lot
        # 1) thresholding; adjusted from 100 to 80, since sigmoid of [-]100
        #    causes overflow with IEEE single precision floats (max ~10e38)
        raw_scores[raw_scores < -RAW_SCORE_LIMIT] = -RAW_SCORE_LIMIT
        raw_scores[raw_scores > RAW_SCORE_LIMIT] = RAW_SCORE_LIMIT
        # 2) apply sigmoid function on clipped confidence scores
        return 1 / (1 + np.exp(-raw_scores))
    def ssd_generate_anchors(self,opts: dict) -> np.ndarray:
        """This is a trimmed down version of the C++ code; all irrelevant parts
        have been removed.
        (reference: mediapipe/calculators/tflite/ssd_anchors_calculator.cc)
        """
        layer_id = 0
        num_layers = opts['num_layers']
        strides = opts['strides']
        assert len(strides) == num_layers
        input_height = opts['input_size_height']
        input_width = opts['input_size_width']
        anchor_offset_x = opts['anchor_offset_x']
        anchor_offset_y = opts['anchor_offset_y']
        interpolated_scale_aspect_ratio = opts['interpolated_scale_aspect_ratio']
        anchors = []
        while layer_id < num_layers:
            last_same_stride_layer = layer_id
            repeats = 0
            while (last_same_stride_layer < num_layers and
                   strides[last_same_stride_layer] == strides[layer_id]):
                last_same_stride_layer += 1
                # aspect_ratios are added twice per iteration
                repeats += 2 if interpolated_scale_aspect_ratio == 1.0 else 1
            stride = strides[layer_id]
            feature_map_height = input_height // stride
            feature_map_width = input_width // stride
            for y in range(feature_map_height):
                y_center = (y + anchor_offset_y) / feature_map_height
                for x in range(feature_map_width):
                    x_center = (x + anchor_offset_x) / feature_map_width
                    for _ in range(repeats):
                        anchors.append((x_center, y_center))
            layer_id = last_same_stride_layer
        return np.array(anchors, dtype=np.float32)
    def __init__(
        self,
        model_path
    ) :
        ssd_opts_full = {
            'num_layers': 4,
            'input_size_height': 128,
            'input_size_width': 128,
            'anchor_offset_x': 0.5,
            'anchor_offset_y': 0.5,
            'strides': [8, 16, 16, 16],
            'interpolated_scale_aspect_ratio': 1.0
        }

        #这里需要封装
        self.tf_model=TensorFlowModel()
        self.tf_model.load(model_path)
        self.input_shape=self.tf_model.get_input_shape()
        # self.interpreter = tf.lite.Interpreter(model_path=model_path)
        # self.interpreter.allocate_tensors()
        # self.input_index = self.interpreter.get_input_details()[0]['index']
        # self.input_shape = self.interpreter.get_input_details()[0]['shape']
        # self.bbox_index = self.interpreter.get_output_details()[0]['index']
        # self.score_index = self.interpreter.get_output_details()[1]['index']
        #这里需要封装
        self.anchors = self.ssd_generate_anchors(ssd_opts_full)

    def __call__(
        self,
        image
    ):
        """Run inference and return detections from a given image

        Args:
            image (Image|ndarray|str): Numpy array of shape
                `(height, width, 3)`, PIL Image instance or file name.

        Returns:
            (list) List of detection results with relative coordinates.
        """
        height, width = self.input_shape[1:3]
        tensor_data,original_size,pad_size  = FaceDetection.image_to_tensor(
            image,
            output_size=(width, height),
            keep_aspect_ratio=True,
            output_range=(-1, 1))
        #这里需要不同的处理方式封装到tensorflow模块中
        input_data= tensor_data[np.newaxis]
        # self.interpreter.set_tensor(self.input_index, input_data)
        # self.interpreter.invoke()
        # raw_boxes = self.interpreter.get_tensor(self.bbox_index)
        # raw_scores = self.interpreter.get_tensor(self.score_index)
        raw_boxes,raw_scores=self.tf_model.pred(input_data)
        #这里需要封装一下
        boxes = self._decode_boxes(raw_boxes)
        scores = self._get_sigmoid_scores(raw_scores)
        detections = FaceDetection._convert_to_detections(boxes, scores)
        pruned_detections = non_maximum_suppression(
                                detections,
                                MIN_SUPPRESSION_THRESHOLD, MIN_SCORE,
                                weighted=True)
        #这里做一个更改不在将得分高的放在前面而是排序成，尺寸大的放在前面

        pruned_detections.sort(key=lambda detection: detection.bbox.height,reverse=True)
        return pruned_detections
    @staticmethod
    def _convert_to_detections(
        boxes: np.ndarray,
        scores: np.ndarray
    ) -> List[Detection]:
        """Apply detection threshold, filter invalid boxes and return
        detection instance.
        """
        # return whether width and height are positive
        def is_valid(box: np.ndarray) -> bool:
            return np.all(box[1] > box[0])

        score_above_threshold = scores > MIN_SCORE
        filtered_boxes = boxes[np.argwhere(score_above_threshold)[:, 1], :]
        filtered_scores = scores[score_above_threshold]
        return [Detection(box, score)
                for box, score in zip(filtered_boxes, filtered_scores)
                if is_valid(box)]

    @staticmethod
    def image_to_tensor(
            img,
            output_size,
            keep_aspect_ratio,
            output_range: Tuple[float, float] = (0., 1.),
    ):
        original_height, orginal_width = img.shape[0:2]
        new_width, new_height = img.shape[0:2]
        pad_x, pad_y = 0, 0
        if keep_aspect_ratio:
            if orginal_width > original_height:
                new_height = orginal_width
                pad_y = new_height - original_height
            else:
                new_width = original_height
                pad_x = new_width - orginal_width
        padded_image = cv2.copyMakeBorder(img, 0, pad_y, 0, pad_x, cv2.BORDER_CONSTANT, (0, 0, 0))
        padded_image = cv2.resize(padded_image, output_size)
        # finally, apply value range transform
        min_val, max_val = output_range
        tensor_data = np.asarray(padded_image, dtype=np.float32)
        tensor_data *= (max_val - min_val) / 255
        tensor_data += min_val
        return tensor_data, (original_height, orginal_width), (pad_y, pad_x)

    @staticmethod
    def collect_face_info(data):
        face_info = {}
        for index, item in enumerate(data):
            if isinstance(item, Point):
                face_info[str(index)] = (int(item.x), int(item.y))
            elif isinstance(item, RectOrOval):
                face_info["rect"] = (int(item.left), int(item.top), int(item.right), int(item.bottom))

        return FaceDetection.getsture_recognize(face_info)


    @staticmethod
    def render_to_image(
            annotations,
            image,
    ):
        # top_left=[0,0]
        # bottom_right=[1,1]
        for annotation in annotations:
            if annotation.normalized_positions:
                scaled = annotation.scaled((max(image.shape), max(image.shape)))
            else:
                scaled = annotation
            if not len(scaled.data):
                continue
            thickness = int(scaled.thickness)
            color = scaled.color
            # import pdb
            # pdb.set_trace()
            gesture_id=FaceDetection.collect_face_info(scaled.data)
            # print("gesture_id:{}".format(gesture_id))
            if gesture_id==1:
                color=Colors.PINK
            elif gesture_id==2 or gesture_id==3:
                color=Colors.GREEN
            elif gesture_id==4 or gesture_id==5:
                color = Colors.BLUE
            else:
                color=Colors.BLACK
            for index,item in enumerate(scaled.data):
                if isinstance(item, Point):

                    image = cv2.circle(image, (int(item.x), int(item.y)), radius=2, color=color.as_tuple,
                                       thickness=thickness)

                    #cv2.putText(image, str(index), (int(item.x), int(item.y) - 2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 2)

                elif isinstance(item, RectOrOval):
                    #
                    image = cv2.rectangle(image, pt1=(int(item.left), int(item.top)),
                                          pt2=(int(item.right), int(item.bottom)),
                                          color=color.as_tuple, thickness=thickness)
                    # top_left=(int(item.left), int(item.top))
                    # bottom_right=(int(item.right), int(item.bottom))
                else:
                    # don't know how to render this
                    pass
        # original_height, original_width = image.shape[:2]
        # x1, y1 = top_left  # 左上角坐标
        # x2, y2 = bottom_right  # 右下角坐标
        # subimage=image[y1:y2, x1:x2]
        # # 将子图拉伸回原始图像的大小
        # resized_subimage = cv2.resize(subimage, (original_width, original_height), interpolation=cv2.INTER_LINEAR)

        # return resized_subimage,gesture_id
        return image,gesture_id

        # return image[face_info["rect"][1]:face_info["rect"][3], face_info["rect"][0]:face_info["rect"][2]], face_info


    @staticmethod
    def detections_to_render_data(
            detections,
            bounds_color,
            keypoint_color,
            line_width=1,
            point_width=3,
            normalized_positions=True,
    ):

        def to_rect(detection: Detection) -> RectOrOval:
            bbox = detection.bbox
            return RectOrOval(bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax)

        annotations = []
        if bounds_color is not None and line_width > 0:
            bounds = Annotation([to_rect(detection) for detection in detections],
                                normalized_positions, thickness=line_width,
                                color=bounds_color)
            annotations.append(bounds)
        if keypoint_color is not None and point_width > 0:
            points = Annotation([Point(x, y)
                                 for detection in detections
                                 for (x, y) in detection],
                                normalized_positions, thickness=point_width,
                                color=keypoint_color)
            annotations.append(points)

        return annotations

def main():
    model_path = r'faceModel/face_detection_short_range.tflite'
    img_path=r"D:\my\res\testface"
    result_path=r"D:\my\res\testfaceresult"
    # image = Image.open(r'demo128.jpg')

    detect_faces = FaceDetection(model_path)
    filenames=os.listdir(img_path)
    for filename in filenames:
        start_time=time.time()
        image = cv2.imread(os.path.join(img_path,filename))
        faces=detect_faces(image)
        print("cost time :{}".format(time.time()-start_time))
        if not len(faces):
            print('no faces detected :(')
        else:
            print("{} faces were found".format(len(faces)))
            #这一段是给到显示的
            render_data = FaceDetection.detections_to_render_data(faces, bounds_color=Colors.GREEN, keypoint_color=Colors.RED)
            result,face_pos = FaceDetection.render_to_image(render_data, image)
            #result是图像,point是真实坐标点位置
            cv2.imwrite(os.path.join(result_path,filename), result)
            # print(face_pos)
if __name__=="__main__":
    main()
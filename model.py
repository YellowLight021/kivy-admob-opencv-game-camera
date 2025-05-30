import numpy as np
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass

    File = autoclass('java.io.File')
    Interpreter = autoclass('org.tensorflow.lite.Interpreter')
    InterpreterOptions = autoclass('org.tensorflow.lite.Interpreter$Options')
    Tensor = autoclass('org.tensorflow.lite.Tensor')
    DataType = autoclass('org.tensorflow.lite.DataType')
    TensorBuffer = autoclass('org.tensorflow.lite.support.tensorbuffer.TensorBuffer')
    ByteBuffer = autoclass('java.nio.ByteBuffer')


    class TensorFlowModel():
        def load(self, model_filename, num_threads=None):
            model = File(model_filename)
            options = InterpreterOptions()
            if num_threads is not None:
                options.setNumThreads(num_threads)
            self.interpreter = Interpreter(model, options)
            self.allocate_tensors()

        def allocate_tensors(self):
            self.interpreter.allocateTensors()
            self.input_shape = self.interpreter.getInputTensor(0).shape()
            self.output_shapes = [self.interpreter.getOutputTensor(i).shape() for i in
                                  range(self.interpreter.getOutputTensorCount())]
            self.output_types = [self.interpreter.getOutputTensor(i).dataType() for i in
                                 range(self.interpreter.getOutputTensorCount())]

        def get_input_shape(self):
            return self.input_shape

        def resize_input(self, shape):
            if self.input_shape != shape:
                self.interpreter.resizeInput(0, shape)
                self.allocate_tensors()

        def pred(self, x):
            # assumes one input and two outputs
            input = ByteBuffer.wrap(x.tobytes())

            # 运行模型（不直接返回输出）
            self.interpreter.run(input, None)

            # 获取输出张量缓冲区并手动读取内容
            output_0_buffer = self.interpreter.getOutputTensor(0).asReadOnlyBuffer()
            output_1_buffer = self.interpreter.getOutputTensor(1).asReadOnlyBuffer()

            # 手动逐字节读取 ByteBuffer 内容并转成 numpy 数组
            output_0_bytes = bytearray(output_0_buffer.remaining())
            output_1_bytes = bytearray(output_1_buffer.remaining())
            output_0_buffer.get(output_0_bytes)
            output_1_buffer.get(output_1_bytes)

            # 将字节数组转换为 numpy 数组
            output_0 = np.frombuffer(output_0_bytes, dtype=np.float32).reshape(self.output_shapes[0])
            output_1 = np.frombuffer(output_1_bytes, dtype=np.float32).reshape(self.output_shapes[1])
            return output_0,output_1

elif platform == 'ios':
    from pyobjus import autoclass, objc_arr
    from ctypes import c_float, cast, POINTER

    NSString = autoclass('NSString')
    NSError = autoclass('NSError')
    Interpreter = autoclass('TFLInterpreter')
    InterpreterOptions = autoclass('TFLInterpreterOptions')
    NSData = autoclass('NSData')
    NSMutableArray = autoclass("NSMutableArray")

    class TensorFlowModel:
        def load(self, model_filename, num_threads=None):
            self.error = NSError.alloc()
            model = NSString.stringWithUTF8String_(model_filename)
            options = InterpreterOptions.alloc().init()
            if num_threads is not None:
                options.numberOfThreads = num_threads
            self.interpreter = Interpreter.alloc(
            ).initWithModelPath_options_error_(model, options, self.error)
            self.allocate_tensors()

        def allocate_tensors(self):
            self.interpreter.allocateTensorsWithError_(self.error)
            self.input_shape = self.interpreter.inputTensorAtIndex_error_(
                0, self.error).shapeWithError_(self.error)
            self.input_shape = [
                self.input_shape.objectAtIndex_(_).intValue()
                for _ in range(self.input_shape.count())
            ]
            self.output_shape = self.interpreter.outputTensorAtIndex_error_(
                0, self.error).shapeWithError_(self.error)
            self.output_shape = [
                self.output_shape.objectAtIndex_(_).intValue()
                for _ in range(self.output_shape.count())
            ]
            self.output_type = self.interpreter.outputTensorAtIndex_error_(
                0, self.error).dataType

        def get_input_shape(self):
            return self.input_shape

        def resize_input(self, shape):
            if self.input_shape != shape:
                # workaround as objc_arr doesn't work as expected on iPhone
                array = NSMutableArray.new()
                for x in shape:
                    array.addObject_(x)
                self.interpreter.resizeInputTensorAtIndex_toShape_error_(
                    0, array, self.error)
                self.allocate_tensors()

        def pred(self, x):
            # assumes one input and one output for now
            bytestr = x.tobytes()
            # must cast to ctype._SimpleCData so that pyobjus passes pointer
            floatbuf = cast(bytestr, POINTER(c_float)).contents
            data = NSData.dataWithBytes_length_(floatbuf, len(bytestr))
            print(dir(self.interpreter))
            self.interpreter.copyData_toInputTensor_error_(
                data, self.interpreter.inputTensorAtIndex_error_(
                    0, self.error), self.error)
            self.interpreter.invokeWithError_(self.error)
            output = self.interpreter.outputTensorAtIndex_error_(
                0, self.error).dataWithError_(self.error).bytes()
            # have to do this to avoid memory leaks...
            while data.retainCount() > 1:
                data.release()
            return np.reshape(
                np.frombuffer(
                    (c_float * np.prod(self.output_shape)).from_address(
                        output.arg_ref), c_float), self.output_shape)

else:
    import tensorflow as tf

    class TensorFlowModel:
        def load(self, model_path, num_threads=None):
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_index = self.interpreter.get_input_details()[0]['index']
            self.input_shape = self.interpreter.get_input_details()[0]['shape']
            self.bbox_index = self.interpreter.get_output_details()[0]['index']
            self.score_index = self.interpreter.get_output_details()[1]['index']
        def get_input_shape(self):
            return self.input_shape
        def pred(self, input_data):
            self.interpreter.set_tensor(self.input_index, input_data)
            self.interpreter.invoke()
            raw_boxes = self.interpreter.get_tensor(self.bbox_index)
            raw_scores = self.interpreter.get_tensor(self.score_index)
            return [raw_boxes,raw_scores]

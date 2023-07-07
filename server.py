"""
像Gradio一样的输入输出定义方式？
比如：[image, text]之类的
"""
from flask import Flask, request, make_response
from typing import Any, Callable, Dict, List, Optional, Type, Union
from builder.utils import check_elements_in_list
import inspect
from io import BytesIO
import base64
import cv2
import numpy as np
import json

app = Flask("app")

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return json.JSONEncoder.default(self, obj)

def bytes_encoder(obj):
    if isinstance(obj, bytes):
        return obj.decode('utf-8')  # 将字节流转换为字符串
    raise TypeError("Object of type {} is not JSON serializable".format(type(obj)))

class SwanInference():
    def __init__(self):
        self.mode = None
        self.io_types = ["text", "image"]

    def parameters(self,
                   fn: Callable,
                   inputs: Union[list, str, None],
                   outputs: Union[list, str, None]) -> None:
        """
        输入推理函数、输入类型、输出类型，设定推理模式
        """

        # 如果fn是列表，报错
        if isinstance(fn, list):
            raise DeprecationWarning(
                "The `fn` parameter only accepts a single function, support for a list "
                "of functions has been deprecated."
            )
        self.fn = fn

        # 如果输入、输出定义为None或空列表，报错
        if (inputs is None or inputs == []) and (outputs is None or outputs == []):
            raise ValueError("Must provide at least one of `inputs` or `outputs`")
        elif outputs is None or outputs == []:
            outputs = []
            self.mode = "input_only"
        elif inputs is None or inputs == []:
            inputs = []
            self.mode = "output_only"

        assert isinstance(inputs, (str, list))
        assert isinstance(outputs, (str, list))

        # 如果类型是str，转换为list
        if not isinstance(inputs, list):
            inputs = [inputs]
        if not isinstance(outputs, list):
            outputs = [outputs]

        # 类型检查: 输入的类型是否在io_types中
        assert check_elements_in_list(inputs, self.io_types) or inputs == []
        assert check_elements_in_list(outputs, self.io_types) or outputs == []

        self.inputs = inputs
        self.outputs = outputs

        # 得到fn函数的参数名
        self.signature = inspect.signature(self.fn)
        parameters = self.signature.parameters
        self.param_names = [param for param in parameters]

        self.return_type = self.signature.return_annotation

    def prediction(self, **inputs):
        """
        传入的文本是字符串, 传入的图片是File(...)
        """
        #TODO: 对输入类型根据self.inputs_dict做判断
        inputs_keys = list(inputs.keys())
        assert check_elements_in_list(inputs_keys, self.param_names)
        for keys, values in inputs.items():
            if isinstance(values, bytes):
                inputs[keys] = cv2.imdecode(np.frombuffer(values, np.uint8), cv2.IMREAD_UNCHANGED)
            elif isinstance(values, str):
                inputs[keys] = values

        #TODO: 加个空判断
        result = self.fn(**inputs)
        # 判断返回值类型是否为元组
        if isinstance(result, tuple):
            num_variables = len(result)
        else:
            num_variables = 1

        assert num_variables == len(self.outputs), "输出的数量与定义的不一致"

        if num_variables == 1:
            if self.outputs == ["image"]:
                assert isinstance(result, np.ndarray)
                result = cv2.imencode(".jpg", result)[1].tostring()
                result = base64.b64encode(result)
            elif self.outputs == ["text"]:
                assert isinstance(result, str)
            result_json = {"content": result}
        else:
            result = list(result)
            result_json = {}
            for iter, output in enumerate(self.outputs):
                if output == "image":
                    assert isinstance(result[iter], np.ndarray)
                    result[iter] = cv2.imencode(".jpg", result[iter])[1].tostring()
                    result_json[iter] = {"content": base64.b64encode(result[iter])}
                elif output == "text":
                    assert isinstance(result[iter], str)
                    result_json[iter] = {"content": result[iter]}

        return json.dumps(result_json, default=bytes_encoder)

    def launch(self):
        """
        用户的在API端的输入假设是["text", "image"]
        """
        @app.route("/", methods=["POST", "GET"])
        def get_prediction():
            inputs = request.form.to_dict()
            files = request.files
            file_data = {}
            for field_name, file in files.items():
                file_data[field_name] = file.read()
            inputs.update(file_data)
            return self.prediction(**inputs)

        app.run(host="0.0.0.0", port=8000)
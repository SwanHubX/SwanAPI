from flask import Flask, request, make_response
from typing import Any, Callable, Dict, List, Optional, Type, Union
from builder.utils import check_elements_in_list
import inspect
import base64
import cv2
import numpy as np
import json

app = Flask("app")


def bytes_encoder(obj):
    """
    字节流编码
    """
    if isinstance(obj, bytes):
        return obj.decode('utf-8')  # 将字节流转换为字符串
    raise TypeError("Object of type {} is not JSON serializable".format(type(obj)))


class SwanInference:
    def __init__(self):
        self.mode = "both"  # ["both", "input_only", "output_only"]
        self.io_types = ["text", "image"]
        self.fn = None
        self.inputs = None
        self.outputs = None
        self.signature = None
        self.param_names = None
        self.return_type = None

    def type_reset(self, item):
        """根据输入的类型字符串，替换为对应的类型变量"""
        TYPES = {
            "text": str,
            "image": bytes
        }
        return TYPES[item]

    def parameters(self,
                   fn: Callable,
                   inputs: Union[list, str, None] = None,
                   outputs: Union[list, str, None] = None) -> None:
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
        # 如果输出为空，但是输入不为空
        elif outputs is None or outputs == []:
            outputs = []
            self.mode = "input_only"
        # 如果输入为空，但是输出不为空
        elif inputs is None or inputs == []:
            inputs = []
            self.mode = "output_only"

        # 类型检查: 输入、输出的类型是否为str或list, 如果类型是str，转换为list
        assert isinstance(inputs, (str, list))
        assert isinstance(outputs, (str, list))
        if not isinstance(inputs, list):
            inputs = [inputs]
        if not isinstance(outputs, list):
            outputs = [outputs]

        # 类型检查: 输入的类型是否在io_types中
        if self.mode == "both":
            assert check_elements_in_list(inputs, self.io_types)
            assert check_elements_in_list(outputs, self.io_types)
        elif self.mode == "input_only":
            assert check_elements_in_list(inputs, self.io_types)
        else:
            assert check_elements_in_list(outputs, self.io_types)

        # 类型转换: 将输入、输出的类型转换为对应的类型变量
        self.inputs = [self.type_reset(input) for input in inputs]
        self.outputs = outputs

        # 得到fn函数的签名信息
        self.signature = inspect.signature(self.fn)

        # 得到fn函数的参数名
        parameters = self.signature.parameters
        self.param_names = [param for param in parameters]

        # 判断输入的数量是否与定义的一致
        assert len(self.param_names) == len(self.inputs), ValueError("输入的数量与定义的不一致")

        # 得到fn返回值的信息
        self.return_type = self.signature.return_annotation

    def prediction(self, **inputs):
        inputs_keys = list(inputs.keys())
        assert check_elements_in_list(inputs_keys, self.param_names)  # 判断请求输入的参数名是否与定义的一致

        for iter, (keys, values) in enumerate(inputs.items()):
            assert isinstance(values, self.inputs[iter]), "输入的类型与定义的不一致"
            if isinstance(values, bytes):
                print(type(values))
                inputs[keys] = cv2.imdecode(np.frombuffer(values, np.uint8), cv2.IMREAD_UNCHANGED)
            elif isinstance(values, str):
                inputs[keys] = values

        result = self.fn(**inputs)
        # 判断返回值类型是否为元组
        if isinstance(result, tuple):
            num_variables = len(result)
        elif result is None:
            num_variables = 0
        else:
            num_variables = 1

        assert num_variables == len(self.outputs), "输出的数量与定义的不一致"

        # 如果输出的变量数量1
        if num_variables == 1:
            if self.outputs == ["image"]:
                assert isinstance(result, np.ndarray)
                result = cv2.imencode(".jpg", result)[1].tostring()
                result = base64.b64encode(result)
            elif self.outputs == ["text"]:
                assert isinstance(result, str)
            result_json = {"content": result}
        # 如果输出的变量数量>=2
        elif num_variables >= 2:
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
        else:
            result_json = {"content": None}

        return json.dumps(result_json, default=bytes_encoder)

    def launch(self, server_name="0.0.0.0", port=8000):
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

        app.run(host=server_name, port=port)

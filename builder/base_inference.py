from builder.utils import check_elements_in_list, is_float
from typing import Any, Callable, Dict, List, Optional, Type, Union
import inspect
import numpy as np
import cv2
import base64


class BaseInference:
    def __init__(self):
        # self.model's options - ["both", "input_only", "output_only"]
        self.mode = "both"
        self.io_types = ["text", "image", "number"]
        self.fn = None
        self.inputs = None
        self.outputs = None
        self.signature = None
        self.fn_param_names = None
        self.TYPES = {
            "text": str,
            "image": Union[bytes],
            "number": Union[int, float],
        }
        self.inputs_typing = None
        self.outputs_typing = None
        self.prediction_inputs = None
        self.prediction_inputs_keys = None
        self.prediction_output_num_variables = None

    def inference_type_checker(self) -> None:
        # 如果fn是列表，报错
        if isinstance(self.fn, list):
            raise DeprecationWarning(
                "The `fn` parameter only accepts a single function, support for a list "
                "of functions has been deprecated."
            )

        # 如果输入、输出定义为None或空列表，报错
        if (self.inputs is None or self.inputs == []) and (self.outputs is None or self.outputs == []):
            raise ValueError("Must provide at least one of `inputs` or `outputs`")
        # 如果输出为空，但是输入不为空
        elif self.outputs is None or self.outputs == []:
            self.outputs = []
            self.mode = "input_only"
        # 如果输入为空，但是输出不为空
        elif self.inputs is None or self.inputs == []:
            self.inputs = []
            self.mode = "output_only"

        # 类型检查: 输入、输出的类型是否为str或list, 如果类型是str，转换为list
        assert isinstance(self.inputs, (str, list))
        assert isinstance(self.outputs, (str, list))
        if not isinstance(self.inputs, list):
            self.inputs = [self.inputs]
        if not isinstance(self.outputs, list):
            self.outputs = [self.outputs]

        # 类型检查: 输入的类型是否在io_types中
        if self.mode == "both":
            assert check_elements_in_list(self.inputs, self.io_types)
            assert check_elements_in_list(self.outputs, self.io_types)
        elif self.mode == "input_only":
            assert check_elements_in_list(self.inputs, self.io_types)
        else:
            assert check_elements_in_list(self.outputs, self.io_types)

        self.inputs_typing = [self.TYPES[input] for input in self.inputs]

    def get_fn_information(self) -> None:
        # 得到fn函数的签名信息
        self.signature = inspect.signature(self.fn)

        # 得到fn函数的参数名
        self.fn_param_names = [param for param in self.signature.parameters]

        # 判断输入的数量是否与定义的一致
        assert len(self.fn_param_names) == len(self.inputs), ValueError("输入的数量与定义的不一致")

    def prediction_input_type_checker(self, inputs: Dict[str, Any]) -> None:
        self.prediction_inputs = inputs

        self.prediction_inputs_keys = list(self.prediction_inputs.keys())
        assert check_elements_in_list(self.prediction_inputs_keys, self.fn_param_names)  # 判断请求输入的参数名是否与定义的一致

    def prediction_input_converter(self) -> None:
        # 根据post输入类型，做相应的转换
        for iter, (keys, values) in enumerate(self.prediction_inputs.items()):
            # 对于输入的类型为number的情况
            if self.inputs[iter] == self.TYPES["number"]:
                assert is_float(values), "输入的类型与定义的number类型不一致"
                self.prediction_inputs[keys] = float(values)
            # 对于输入的类型为image的情况
            elif type(values) == self.TYPES["image"]:
                self.prediction_inputs[keys] = cv2.imdecode(np.frombuffer(values, np.uint8), cv2.IMREAD_UNCHANGED)
            # 对于输入的类型为text的情况
            elif type(values) == self.TYPES["text"]:
                self.prediction_inputs[keys] = values
            else:
                assert isinstance(values, self.inputs[iter]), "输入的类型与定义的不一致"

    def prediction_output_type_checker(self, result: Any) -> None:
        # 判断返回值类型是否为元组
        if isinstance(result, tuple):
            self.prediction_output_num_variables = len(result)
        elif result is None:
            self.prediction_output_num_variables = 0
        else:
            self.prediction_output_num_variables = 1

        assert self.prediction_output_num_variables == len(self.outputs), "输出的数量与定义的不一致"

    def prediction_output_converter(self, result: Any) -> Dict[str, Any]:
        # 如果输出的变量数量1
        if self.prediction_output_num_variables == 1:
            if self.outputs == ["image"]:
                assert isinstance(result, np.ndarray)
                result = cv2.imencode(".jpg", result)[1].tostring()
                result = base64.b64encode(result)
            elif self.outputs == ["text"]:
                assert isinstance(result, str)
            elif self.outputs == ["number"]:
                assert isinstance(result, (int, float))
            result_json = {"content": result}
        # 如果输出的变量数量>=2
        elif self.prediction_output_num_variables >= 2:
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
                elif output == "number":
                    assert isinstance(result[iter], (int, float))
                    result_json[iter] = {"content": result[iter]}
        else:
            result_json = {"content": None}

        return result_json

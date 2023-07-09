from .utils import check_elements_in_list, is_float, is_list, is_dict
from typing import Any, Callable, Dict, List, Optional, Type, Union
import inspect
import numpy as np
import cv2
import base64


class BaseInference:
    def __init__(self):
        # self.mode's options - ["both", "input_only", "output_only"]
        self.mode = "both"
        self.fn = None
        self.inputs = None
        self.outputs = None
        self.signature = None
        self.fn_param_names = None
        self.TYPES = {
            "text": str,
            "image": Union[bytes, str],
            "number": Union[int, float],
            "list": list,
            "dict": dict,
        }
        self.types_list = list(self.TYPES.keys())
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
            assert check_elements_in_list(self.inputs, self.types_list)
            assert check_elements_in_list(self.outputs, self.types_list)
        elif self.mode == "input_only":
            assert check_elements_in_list(self.inputs, self.types_list)
        else:
            assert check_elements_in_list(self.outputs, self.types_list)

    def get_fn_information(self) -> None:
        # 得到fn函数的签名信息
        self.signature = inspect.signature(self.fn)

        # 得到fn函数的参数名
        self.fn_param_names = [param for param in self.signature.parameters]

        # 判断inputs的数量大于fn定义的数量
        if len(self.fn_param_names) < len(self.inputs):
            raise ValueError("inputs长度不应该大于函数的参数个数")
        else:
            self.fn_param_names = self.fn_param_names[: len(self.inputs)]

    def prediction_input_type_checker(self, inputs: Dict[str, Any]) -> None:
        # 对于网络请求的输入进行检查
        self.prediction_inputs = inputs
        self.prediction_inputs_keys = list(self.prediction_inputs.keys())
        assert len(self.prediction_inputs_keys) == len(self.inputs), "请求传入的参数数量与inputs定义的不一致"
        assert check_elements_in_list(self.prediction_inputs_keys, self.fn_param_names), "请求传入的参数key与fn定义的不一致"

    def prediction_input_converter(self) -> None:
        # 根据post输入类型，做相应的转换
        for iter, param_name in enumerate(self.fn_param_names):
            # param_name : 'input_image', 'custom_size_height', 'custom_size_width'
            values = self.prediction_inputs[param_name]
            # 对于输入的类型为image的情况
            if self.inputs[iter] == "image":
                if isinstance(values, bytes):
                    self.prediction_inputs[param_name] = cv2.imdecode(np.frombuffer(values, np.uint8), cv2.IMREAD_UNCHANGED)
                # 如果输入的是字符串，则作为图像路径处理
                elif isinstance(values, str):
                    self.prediction_inputs[param_name] = cv2.imread(values, cv2.IMREAD_UNCHANGED)
                else:
                    raise TypeError("输入的类型与定义的image类型不一致")

            # 对于输入的类型为number的情况
            elif self.inputs[iter] == "number":
                assert is_float(values), "输入的类型与定义的number类型不一致"
                self.prediction_inputs[param_name] = float(values)
            # 对于输入的类型为text的情况
            elif self.inputs[iter] == "text":
                assert isinstance(values, str), "输入的类型与定义的text类型不一致"
                self.prediction_inputs[param_name] = values
            # 对于输入的类型为list的情况
            elif self.inputs[iter] == "list":
                self.prediction_inputs[param_name] = is_list(values)
            # 对于输入的类型为dict的情况
            elif self.inputs[iter] == self.TYPES["dict"]:
                self.prediction_inputs[param_name] = is_dict(values)
            else:
                raise TypeError("输入的类型与定义的不一致")

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
            if result is None:
                result = None
            elif self.outputs == ["image"]:
                assert isinstance(result, np.ndarray)
                result = cv2.imencode(".jpg", result)[1].tostring()
                result = base64.b64encode(result)
            elif self.outputs == ["text"]:
                assert isinstance(result, str)
            elif self.outputs == ["number"]:
                assert isinstance(result, (int, float))
            elif self.outputs == ["dict"]:
                assert isinstance(result, dict)
            elif self.outputs == ["list"]:
                assert isinstance(result, list)
            result_json = {"content": result}
        # 如果输出的变量数量>=2
        elif self.prediction_output_num_variables >= 2:
            result = list(result)
            result_json = {}
            for iter, output in enumerate(self.outputs):
                if result[iter] is None:
                    result_json[iter] = {"content": None}
                elif output == "image":
                    assert isinstance(result[iter], np.ndarray)
                    result[iter] = cv2.imencode(".jpg", result[iter])[1].tostring()
                    result_json[iter] = {"content": base64.b64encode(result[iter])}
                elif output == "text":
                    assert isinstance(result[iter], str)
                    result_json[iter] = {"content": result[iter]}
                elif output == "number":
                    assert isinstance(result[iter], (int, float))
                    result_json[iter] = {"content": result[iter]}
                elif self.outputs == ["dict"]:
                    assert isinstance(result, dict)
                    result_json[iter] = {"content": result[iter]}
                elif self.outputs == ["list"]:
                    assert isinstance(result, list)
                    result_json[iter] = {"content": result[iter]}
        else:
            result_json = {"content": None}

        return result_json

from .utils import utils
from typing import Any, Callable, Dict, List, Optional, Type, Union
import inspect
import numpy as np
from PIL import Image as _Image
from pathlib import Path


class BaseInference:
    def __init__(self):
        # self.mode's options - ["both", "input_only", "output_only"]
        self.mode = "both"
        self.fn = None
        self.backbone_inputs = None
        self.backbone_outputs = None
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
        self.requests_inputs = None
        self.requests_inputs_param_names = None
        self.requests_outputs_variables_num = None

    def backbone_type_checker(self) -> None:
        # 如果fn是列表，报错
        if isinstance(self.fn, list):
            raise DeprecationWarning(
                "The `fn` parameter only accepts a single function, support for a list "
                "of functions has been deprecated."
            )

        # 如果输入、输出定义为None或空列表，报错
        if (self.backbone_inputs is None or self.backbone_inputs == []) and \
                (self.backbone_outputs is None or self.backbone_outputs == []):
            raise ValueError("Must provide at least one of `inputs` or `outputs`")
        # 如果输出为空，但是输入不为空
        elif self.backbone_outputs is None or self.backbone_outputs == []:
            self.backbone_outputs = []
            self.mode = "input_only"
        # 如果输入为空，但是输出不为空
        elif self.backbone_inputs is None or self.backbone_inputs == []:
            self.backbone_inputs = []
            self.mode = "output_only"

        # 类型检查: 输入、输出的类型是否为str或list, 如果类型是str，转换为list
        assert isinstance(self.backbone_inputs, (str, list))
        assert isinstance(self.backbone_outputs, (str, list))
        if not isinstance(self.backbone_inputs, list):
            self.backbone_inputs = [self.backbone_inputs]
        if not isinstance(self.backbone_outputs, list):
            self.backbone_outputs = [self.backbone_outputs]

        # 类型检查: 输入的类型是否在self.types_list中
        if self.mode == "both":
            assert utils.check_elements_in_list(self.backbone_inputs, self.types_list)
            assert utils.check_elements_in_list(self.backbone_outputs, self.types_list)
        elif self.mode == "input_only":
            assert utils.check_elements_in_list(self.backbone_inputs, self.types_list)
        else:
            assert utils.check_elements_in_list(self.backbone_outputs, self.types_list)

    def backbone_get_fn_parameters(self) -> None:
        # 使用inspect库，得到fn函数的签名变量
        signature = inspect.signature(self.fn)

        # 得到fn函数的参数名列表，形如["input_image", "input_text"]
        self.fn_param_names = [param for param in signature.parameters]

        # 判断inputs的数量是否大于fn定义的数量
        # 如果大于，则报错
        # 如果小于，则截取fn定义的前len(inputs)个参数
        if len(self.fn_param_names) < len(self.backbone_inputs):
            raise ValueError("SwanInference中inputs的长度不应该大于fn的参数个数")
        else:
            self.fn_param_names = self.fn_param_names[: len(self.backbone_inputs)]

    def requests_input_type_checker(self, requests_inputs: Dict[str, Any]) -> None:
        """
        检查网络请求的输入参数：
        1. 长度是否合格-与len(self.backbones)相等
        2. 参数名是否与self.fn_param_names匹配
        """
        # self.requests_inputs - 用户输入的完整json字典
        self.requests_inputs = requests_inputs
        # 获取网络请求的参数个数
        self.requests_inputs_param_names = list(self.requests_inputs.keys())
        # 判断网络请求输入的参数的个数是否与inputs定义的个数一致
        assert len(self.requests_inputs_param_names) == len(self.backbone_inputs), "请求传入的参数数量与inputs定义的不一致"
        # 判断网络请求输入的参数名是否与fn定义的一致
        assert utils.check_elements_in_list(self.requests_inputs_param_names, self.fn_param_names), "请求传入的参数key与fn定义的不一致"

    def requests_input_converter(self) -> None:
        # 对于每一个requests内容的输入类型，做相应的转换
        for iter, param_name in enumerate(self.fn_param_names):
            # param_name : 'input_image', 'custom_size_height', 'custom_size_width'
            # 获取内容values
            values = self.requests_inputs[param_name]
            # 对于输入的类型为image的情况
            if self.backbone_inputs[iter] == "image":
                # 如果输入的是字节流，则使用imdecode解码图像
                if isinstance(values, bytes):
                    self.requests_inputs[param_name] = utils.bytes_to_array(values)
                # 如果输入的是字符串，则作为图像路径处理，使用Imread读取图像
                elif isinstance(values, str):
                    im = _Image.open(values)
                    self.requests_inputs[param_name] = np.array(im)
                else:
                    raise TypeError("网络请求中{}的类型与定义的image类型不一致".format(param_name))

            # 对于输入的类型为number的情况
            elif self.backbone_inputs[iter] == "number":
                assert utils.is_float(values), "网络请求中{}的类型与定义的number类型不一致".format(param_name)
                self.requests_inputs[param_name] = float(values)

            # 对于输入的类型为text的情况
            elif self.backbone_inputs[iter] == "text":
                assert isinstance(values, str), "网络请求中{}的类型与定义的text类型不一致".format(param_name)
                self.requests_inputs[param_name] = values

            # 对于输入的类型为list的情况
            elif self.backbone_inputs[iter] == "list":
                self.requests_inputs[param_name] = utils.is_list(values)

            # 对于输入的类型为dict的情况
            elif self.backbone_inputs[iter] == "dict":
                self.requests_inputs[param_name] = utils.is_dict(values)

            else:
                raise TypeError("backbone_type_checker have BUGs")

    def requests_output_type_checker(self, result: Any) -> None:
        # 根据result得到返回变量数量
        if isinstance(result, tuple):
            self.requests_outputs_variables_num = len(result)
        else:
            self.requests_outputs_variables_num = 1

        assert self.requests_outputs_variables_num >= len(self.backbone_outputs), "fn返回结果的数量不能小于backbone_outputs的数量"

    def requests_output_converter(self, result: Any) -> Union[Dict[str, Any], None]:
        if self.requests_outputs_variables_num == 1:
            result = [result]
        else:
            result = list(result)

        if len(self.backbone_outputs) == 0:
            return None

        result_json = {}
        for iter, backbone_output in enumerate(self.backbone_outputs):
            if result[iter] is None:
                result_json[iter] = {"content": None}
            elif backbone_output == "image":
                y = result[iter]
                if isinstance(y, np.ndarray):
                    im_base64 = utils.encode_array_to_base64(y)
                elif isinstance(y, _Image.Image):
                    im_base64 = utils.encode_pil_to_base64(y)
                elif isinstance(y, (str, Path)):
                    im_base64 = utils.encode_url_or_file_to_base64(y)
                else:
                    raise ValueError("Cannot process this value as an Image")
                result_json[iter] = {"content": im_base64}

            elif backbone_output == "text":
                assert isinstance(result[iter], str)
                result_json[iter] = {"content": result[iter]}

            elif backbone_output == "number":
                assert isinstance(result[iter], (int, float))
                result_json[iter] = {"content": result[iter]}

            elif backbone_output == ["dict"]:
                assert isinstance(result, dict)
                result_json[iter] = {"content": result[iter]}

            elif backbone_output == ["list"]:
                assert isinstance(result, list)
                result_json[iter] = {"content": result[iter]}

            else:
                raise TypeError("类型检查模块存在Bug")

        return result_json

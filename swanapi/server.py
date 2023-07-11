from flask import Flask, request
from typing import Any, Callable, Dict, List, Optional, Type, Union
from .utils import utils
from .base_inference import BaseInference
import json

app = Flask("SwanAPI Server")


class SwanInference(BaseInference):
    """
    我们将分为两个生命周期：
    1. Backbone: 以fn, inputs和outputs为基础，构建一个推理骨架
    2. Requests: 接受Web请求，将Web请求转换为推理函数的输入，将推理函数的输出转换为Web请求的输出
    """

    def __init__(self):
        super().__init__()

    def inference(self,
                  fn: Callable,
                  inputs: Union[list, str, None] = None,
                  outputs: Union[list, str, None] = None,
                  description: str = None
                  ) -> None:
        """
        用户构建backbone的入口函数
        """
        self.fn = fn
        self.backbone_inputs = inputs
        self.backbone_outputs = outputs
        self.description = description
        self.backbone()

    def backbone(self) -> None:
        """
        以fn, inputs和outputs为基础，构建一个推理骨架Backbone
        """
        # 检查fn、inputs和outputs的类型是否符合规范
        self.backbone_type_checker()
        # 得到fn的形参名称
        self.backbone_get_fn_parameters()

    def requests(self, **inputs):
        # 检查Web输入的类型是否符合Backbone定义的输入类型
        self.requests_input_type_checker(inputs)
        # 根据类型转换为符合Backbone定义的输入类型
        self.requests_input_converter()
        # 调用fn, 得到结果
        result = self.fn(**self.requests_inputs)

        # 检查结果是否符合Backbone定义的输出类型
        self.requests_output_type_checker(result)
        # 根据Backbone定义的输出类型进行转换
        result_json = self.requests_output_converter(result)

        # 将结果转换为json格式
        return json.dumps(result_json, default=utils.bytes_encoder)

    def launch(self,
               server_name: str = "0.0.0.0",
               port: int = 8000
               ) -> None:
        """
        启动Web服务, 基于Flask
        :param server_name: 又被称为Host, 表示IP地址
        :param port: 端口号
        """

        @app.route("/predictions/", methods=["POST", "GET"])
        def get_prediction():
            inputs = request.form.to_dict()
            files = request.files
            file_data = {}
            for field_name, file in files.items():
                file_data[field_name] = file.read()
            inputs.update(file_data)
            return self.requests(**inputs)

        app.run(host=server_name, port=port)

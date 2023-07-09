from flask import Flask, request
from typing import Any, Callable, Dict, List, Optional, Type, Union
from .utils import bytes_encoder
from .base_inference import BaseInference
import json

app = Flask("app")


class SwanInference(BaseInference):
    def __init__(self):
        super().__init__()

    def inference(self,
                  fn: Callable,
                  inputs: Union[list[str], str, None],
                  outputs: Union[list[str], str, None],
                  description: str
                  ) -> None:
        self.fn = fn
        self.inputs = inputs
        self.outputs = outputs

        # 检查fn、inputs和outputs的类型是否符合规范
        self.inference_type_checker()
        # 得到fn的形参名称
        self.get_fn_information()

    def prediction(self, **inputs):
        # 检查Web输入的类型是否符合规范
        self.prediction_input_type_checker(inputs)
        # 根据类型转换为推理函数的输入
        self.prediction_input_converter()

        result = self.fn(**self.prediction_inputs)

        self.prediction_output_type_checker(result)
        result_json = self.prediction_output_converter(result)

        return json.dumps(result_json, default=bytes_encoder)

    def launch(self,
               server_name="0.0.0.0",
               port=8000
               ):
        @app.route("/predictions/", methods=["POST", "GET"])
        def get_prediction():
            inputs = request.form.to_dict()
            files = request.files
            file_data = {}
            for field_name, file in files.items():
                file_data[field_name] = file.read()
            inputs.update(file_data)
            return self.prediction(**inputs)

        app.run(host=server_name, port=port)

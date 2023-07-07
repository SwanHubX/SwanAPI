"""
像Gradio一样的输入输出定义方式？
比如：[image, text]之类的
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Any, Callable, Dict, List, Optional, Type, Union
import inspect
from io import BytesIO
import cv2
import numpy as np

app = FastAPI()


class SwanInference():
    def __init__(self):
        self.mode = None

    def parameters(self,
                   fn: Callable,
                   inputs: Union[list, str],
                   outputs: Union[list, str]):
        """
        输入推理函数、输入类型、输出类型，设定推理模式
        :param fn:
        :param inputs:
        :param outputs:
        :return:
        """

        # 如果fn是列表，报错
        if isinstance(fn, list):
            raise DeprecationWarning(
                "The `fn` parameter only accepts a single function, support for a list "
                "of functions has been deprecated."
            )
        if not isinstance(inputs, list):
            inputs = [inputs]
        if not isinstance(outputs, list):
            outputs = [outputs]

        if inputs == ["text"] and outputs == ["image"]:
            self.mode = "text2image"

            def prediction(text: str):
                return self.text2image(fn, text)

        elif inputs == ["image"] and outputs == ["image"]:
            self.mode = "image2image"

            def prediction(input_image: np.ndarray):
                return self.image2image(fn, input_image)
        else:
            raise ValueError("Please check your input and output type.")

        self.inferece_fn = prediction

    def text2image(self, fn, text: str):
        output_image = fn(text)
        output_image = cv2.imencode(".png", output_image)[1].tobytes()
        return StreamingResponse(BytesIO(output_image), media_type="image/png")

    def image2image(self, fn, image):
        output_image = fn(image)
        output_image = cv2.imencode(".png", output_image)[1].tobytes()
        return StreamingResponse(BytesIO(output_image), media_type="image/png")

    def launch(self):
        @app.post("/")
        def get_prediction(
                text: Optional[str] = None,
                image: UploadFile = File(...)):
            if self.mode == "text2image":
                return self.inferece_fn(text)
            elif self.mode == "image2image":
                content = image.file.read()
                input_image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_UNCHANGED)
                return self.inferece_fn(input_image)
            else:
                raise ValueError("Please check your input and output type.")

        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)

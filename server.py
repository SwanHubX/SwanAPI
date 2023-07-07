"""
像Gradio一样的输入输出定义方式？
比如：[image, text]之类的
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Any, Callable, Dict, List, Optional, Type, Union
import inspect
from io import BytesIO
from builder.runner import Runner
import cv2

app = FastAPI()


class SwanInference():
    def parameters(self,
                   fn: Callable,
                   inputs: list,
                   outputs: list):
        # 如果fn是列表，报错
        if isinstance(fn, list):
            raise DeprecationWarning(
                "The `fn` parameter only accepts a single function, support for a list "
                "of functions has been deprecated. Please use gradio.mix.Parallel "
                "instead."
            )
        if not isinstance(inputs, list):
            inputs = [inputs]
        if not isinstance(outputs, list):
            outputs = [outputs]

        if inputs == ["text"] and outputs == ["image"]:
            def prediction(text: str):
                return self.text2image(fn, text)

            self.inferece_fn = prediction

    def prediction(self, text):
        return self.inferece_fn(text)

    def text2image(self, fn, text: str):
        output_image = fn(text)
        output_image = cv2.imencode(".png", output_image)[1].tobytes()
        return StreamingResponse(BytesIO(output_image), media_type="image/png")

    def launch(self):

        @app.get("/predictions/{text:path}")
        def get_prediction(text: str):
            return self.prediction(text)

        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)

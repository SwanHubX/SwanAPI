"""
像Gradio一样的输入输出定义方式？
比如：[image, text]之类的
"""
from fastapi import FastAPI, UploadFile, File
from predict import Inference
import inspect

app = FastAPI()


class Prediction(Inference):
    def __init__(self):
        self.parameters = inspect.signature(super().predict).parameters
        print(len(self.parameters))
        for name, parameter in self.parameters.items():
            print(f"Parameter name: {name}")
            print(f"Parameter type: {parameter.annotation}")

    def test(self):
        return super().predict()


@app.get("/predictions/")
def prediction():
    x = Prediction()
    return x.test()


if __name__ == "__main__":
    x = Prediction()
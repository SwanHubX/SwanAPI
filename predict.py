# from typing import Union
# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import StreamingResponse
# from io import BytesIO
# import numpy as np
# import cv2
from swan_inference import SwanInference
from cog import BasePredictor

"""
Why build A Class - It will connect to the FastAPI
"""

class Inference(SwanInference):
    def setup(self):
        self.model = None

    def predict(self):
        return "Hello world "


#
# @app.post("/cv/")
# async def image_process(file: UploadFile = File(...)):
#     content = await file.read()
#     input_image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
#     input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
#     output_image = cv2.imencode(".png", input_image)[1].tobytes()
#     return StreamingResponse(BytesIO(output_image), media_type="image/png")
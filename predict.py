import io
from typing import Union
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO
import numpy as np
import cv2

app = FastAPI()


@app.post("/cv/")
async def image_process(file: UploadFile = File(...)):
    content = await file.read()
    input_image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    output_image = cv2.imencode(".jpg", input_image)[1].tobytes()
    return StreamingResponse(BytesIO(output_image), media_type="image/jpg")


@app.get("/items/{item_ id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_ id": item_id, "q": q}

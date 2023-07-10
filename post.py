from swanapi import SwanRequests, Files
import base64
import numpy as np
import cv2

response = SwanRequests(
    url="http://127.0.0.1:8000/predictions/",
    inputs={"im": Files("./test.jpg")})
# print(response)
image_base64 = response[str(0)]['content']
# print(image_base64)
nparr = np.frombuffer(base64.b64decode(image_base64), np.uint8)
img_restore = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
cv2.imwrite("output.jpg", img_restore)
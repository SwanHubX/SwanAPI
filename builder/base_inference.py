from abc import ABC, abstractmethod
# 定义类型，增加代码的可读性
from typing import Any, Callable, Dict, List, Optional, Type, Union

# 让用户封装这么一个类的目的是方便后续SwanAPI的本地与云端推理

# @app.post("/cv/")
# async def image_process(file: UploadFile = File(...)):
#     content = await file.read()
#     input_image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
#     input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
#     output_image = cv2.imencode(".png", input_image)[1].tobytes()
#     return StreamingResponse(BytesIO(output_image), media_type="image/png")

# 推理基类
class BaseInference(ABC):
    @abstractmethod
    def predict(self, **kwargs: Any) -> Any:
        """
        Run a single prediction on the model
        """
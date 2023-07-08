<div align="center">
<img src="assets/logo.png" width="600">
</div>

# SwanAPI

A fast machine learning project [cloud/local] API tool.

## Intended function

1. One-stop packaging of deep learning images

   - Simply write configuration files and inference files

   - No worries about installing mainstream machine learning libraries such as PyTorch, TensorFlow, Transformers, etc.

   - No worries about GPU environment configuration such as CUDA, cudnn, etc.

   - The image runtime will run a high-performance API service for easy invocation.

2. Push images for cloud hosting

3. Generate local debugging GUI interface and API documentation.

## Requirements

- Paython3.7+
- Docker. SwanAPI使用Docker来为你的模型创建容器，在运行SwanAPI之前，你需要[Install Docker](https://docs.docker.com/get-docker/)。

SwanAPI stands on the shoulders of giants:

- [Flask](https://github.com/pallets/flask) for the web backend

## Install

```
pip install swanapi -i https://pypi.org/simple
```

## How it works

Define the Docker environment your model runs in with `swan.yaml`:

```yaml
build:
  gpu: false
  system_packages:
    - "libgl1-mesa-glx"
    - "libglib2.0-0"
  python_version: "3.10"
  python_packages:
    - "numpy"
    - "onnxruntime"
    - "opencv-python"
predict:
  port: 8000
```

如果你在中国，你可以在build下添加`  python_sourece: "cn"`，将使用清华源来安装python_packages。

在`predict.py`中定义你的模型如何推理，我们使用与[Gradio](https://github.com/gradio-app/gradio)相似的代码风格：

```python
import cv2
from swanapi import SwanInference

def predict(image):
    result_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return result_image

if __name__ == "__main__":
    api = SwanInference()
    api.inference(predict,
                  inputs=['image'],
                  outputs=['image'],
                  description="a simple test")
    api.launch()
```

- 2023.7.8:  `v0.1.3`支持`text`, `image`, `number`三种类型

---

现在你可以直接让模型变成预测服务：

```bash
$ python predict.py
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:8000/ (Press CTRL+C to quit)
```

也可以一行命令构建一个深度学习推理镜像：

```bash
$ swanapi build -t my-dl-model
--> Building Docker Image...
--> Building Docker Finish.
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:8000/ (Press CTRL+C to quit)
```

---

请求你的服务（以image-to-image任务为例）：

- Python

```python
import requests
url = "http://127.0.0.1:8000/predictions/"
files = [('image', ('test.jpg', open('./test.jpg', 'rb'), 'image/jpeg'))]
response = requests.request("POST", url, files=files)
print(response.text)
```

- cURL

```bash
curl --location 'http://127.0.0.1:8000/predictions/' \
--form 'image=@"./test.jpf"'
```

得到的json将是：`{"content":"base64"}`

base64解码后即可获得图像文件：

```python
import base64
import numpy as np
import cv2

image_base64 = response.text['content']
nparr = np.fromstring(base64.b64decode(image_base64), np.uint8)
img_restore = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
```


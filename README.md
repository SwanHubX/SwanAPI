<div align="center">
<img src="assets/logo.png" width="600">
</div>





<div align="center">
  <a href="https://pypi.org/project/swanapi" target="_blank">
    <img src="https://img.shields.io/pypi/v/swanapi?color=%2334D058&label=pypi%20package" alt="Package version"></a>
<a href="https://pypi.org/project/fastapi" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fastapi.svg?color=%2334D058" alt="Supported Python versions">
</a>
</div>

<span style="text-align:center; display:inline-block; width:100%">🤖️机器学习项目三行代码变API</span>

<span style="text-align:center; display:inline-block; width:100%">[English](README_EN.md)</span>

## ⬆️预期功能（全力迭代中）

1. 三行代码生成高性能API

2. 轻松打包机器学习API镜像

   - 轻松：仅需增加极少量的代码

   - 打包：无需担心CUDA、cudnn等GPU环境与PyTorch、TensorFlow等机器学习库配置，一键式打包搞定

3. 快速理解与调试：自动创建API文档与调试GUI

4. 调用云端API



## 📚依赖

- Paython3.7+
- Docker. SwanAPI使用Docker来为你的模型创建容器, 在你运行SwanAPI的镜像打包功能之前, 你需要[安装Docker](https://docs.docker.com/get-docker/)。



## 🔧安装

```
pip install swanapi -i https://pypi.org/simple
```



## 💻准备

1⃣️ 在 `swan.yaml`中，定义模型运行的Docker环境：

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

ps：如果你在中国, 可以在build下添加 `python_source: "cn"`以使用清华源安装 `python_packages`.



2⃣️ 在 `predict.py`中, 定义你的模型推理方式。 😄我们使用[Gradio](https://github.com/gradio-app/gradio)的代码风格：

```python
from swanapi import SwanInference
import cv2

# 这是一个简单的图像转黑白的任务
def predict(image):
    result_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return "success", result_image

if __name__ == "__main__":
    api = SwanInference()
    api.inference(predict,
                  inputs=['image'],
                  outputs=['text', 'image'],
                  description="a simple test")
    api.launch()
```

`inputs`和`outputs`支持["text", "image", "number", "list", "dict"]五种类型



## 🚀运行

现在你可以直接将模型转换为预测服务：

```console
$ python predict.py
 * Serving Flask app "SwanAPI Server" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:8000/ (Press CTRL+C to quit)
```

还可以一个命令构建深度学习推理图像，后台将根据`swan.yaml`配置好一切：

```console
$ swanapi build -r -t my-dl-model
--> Building Docker Image...
--> Building Docker Finish.
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:8000/ (Press CTRL+C to quit)
```



## 🚢调用

请求运行好的模型推理服务(以image-to-image任务为例):

- **Python**

```python
import requests
url = "http://127.0.0.1:8000/predictions/"
files = [('image', ('test.jpg', open('./test.jpg', 'rb'), 'image/jpeg'))]
response = requests.request("POST", url, files=files)
print(response.text)
```

你将会收到一个图像编码为base64的Json输出: `{"content":"base64"}`，解码base64后，您将获得图像文件：

```python
import base64
import numpy as np
import cv2

image_base64 = response.text['content']
nparr = np.fromstring(base64.b64decode(image_base64), np.uint8)
img_restore = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
cv2.imwrite("output.jpg", img_restore)
```

---

其他调用方式：

- **cURL**

```bash
curl --location 'http://127.0.0.1:8000/predictions/' \
--form 'image=@"./test.jpg"'
```


from typing import Any, Callable, Dict, List, Optional, Type, Union
import requests
from .swan_types import Files


class BaseRequests:
    """
    增加在Python端快速调用SwanAPI服务的类。
    主要降低API调用的门槛，尤其是对图像等数据类型。
    必要输入：
    - url: str, API的url地址
    - inputs: Json
    - methods: 请求的类型，可选值为["GET", "POST", "PUT", "DELETE"]
    """

    def base_request(self,
                     url: str,
                     inputs: Dict[str, Any] = None,
                     methods: str = "POST"):
        payload = {}
        files = []
        headers = {}

        if inputs is None:
            response = requests.request(methods, url, headers=headers, data=None)
        else:
            for key, value in inputs.items():
                # 如果value的类型是文件类型
                if isinstance(value, Files):
                    files.append((key, value.content()))
                else:
                    payload[key] = value

            inputs_dict = {}
            if len(files) != 0:
                inputs_dict['files'] = files
            if len(payload) != 0:
                inputs_dict['data'] = payload

            response = requests.request(methods, url, headers=headers, **inputs_dict)

        return response.json()

    def post(self,
             url: str,
             inputs: Dict[str, Any] = None,
             ):
        return self.base_request(url, inputs, "POST")

    def get(self,
            url: str,
            inputs: Dict[str, Any] = None,
            ):
        return self.base_request(url, inputs, "get")


def SwanRequests(url: str,
                 inputs: Dict[str, Any] = None,
                 methods: str = "POST"):
    return BaseRequests().base_request(url, inputs, methods)
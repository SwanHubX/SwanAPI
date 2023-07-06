"""
用户predict.py中会嵌套的类
"""
from abc import ABC, abstractmethod
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO
from typing import Any, Callable, Dict, List, Optional, Type, Union


class SwanInference(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def predict(self, **kwargs: Any) -> Any:
        """
        Run a single prediction on the model
        """
"""
以下是模拟用户写的predict.py
"""
from builder.base_inference import BaseInference
import cv2
import numpy as np


class Inference(BaseInference):
    def predict(self, image_path: str) -> np.ndarray:
        input_image = cv2.imread(image_path)
        result_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        return result_image

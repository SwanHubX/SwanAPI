"""
以下是模拟用户写的predict.py
"""
import cv2
from server import SwanInference


def predict(text1, image):
    input_image = image
    result_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    return "success", result_image


if __name__ == "__main__":
    api = SwanInference()
    api.parameters(predict, inputs=["text", "image"], outputs=["text", "image"])
    api.launch()
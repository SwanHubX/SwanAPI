"""
以下是模拟用户写的predict.py
"""
import cv2
from server import SwanInference


def predict(image_path):
    input_image = cv2.imread(image_path)
    result_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    return result_image


if __name__ == "__main__":
    api = SwanInference()
    api.parameters(predict, inputs=["text"], outputs=["image"])
    api.launch()
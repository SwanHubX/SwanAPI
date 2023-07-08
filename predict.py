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

import cv2
from server import SwanInference


def predict(image, number, text):
    input_image = image
    result_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    return "success", result_image, 1


if __name__ == "__main__":
    api = SwanInference()
    api.parameters(predict, inputs=['image', 'number', 'text'], outputs=['text', 'image', 'number'])
    api.launch()

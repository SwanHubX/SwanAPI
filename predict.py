from swanapi import SwanInference
import cv2


# 这是一个简单的图像转黑白的任务
def predict(im):
    result_image = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    return "success", result_image


if __name__ == "__main__":
    api = SwanInference()
    api.inference(predict,
                  inputs=['image'],
                  outputs=['text', 'image'],
                  description="a simple test")
    api.launch()

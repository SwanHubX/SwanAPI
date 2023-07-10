from swanapi import SwanInference


def predict(im, im2, text):
    return im


if __name__ == "__main__":
    api = SwanInference()
    api.inference(predict,
                  inputs=['image', 'image','text'],
                  outputs=['image'],
                  description="a simple test")
    api.launch()

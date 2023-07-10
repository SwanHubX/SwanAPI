from swanapi import SwanInference


def predict(im, text):
    return im, text


if __name__ == "__main__":
    api = SwanInference()
    api.inference(predict,
                  inputs=['image', 'text'],
                  outputs=['image', 'text'],
                  description="a simple test")
    api.launch()

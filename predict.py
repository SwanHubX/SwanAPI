from swanapi import SwanInference


def predict(text):
    print(text)


if __name__ == "__main__":
    api = SwanInference()
    api.inference(predict,
                  inputs=['text'],
                  description="a simple test")
    api.launch()

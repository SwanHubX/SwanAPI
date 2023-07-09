from swanapi import SwanInference
import gradio as gr


def predict(test_dict):
    output_dict = {"a": test_dict[0], "b": 2, "c": 3}
    return output_dict


if __name__ == "__main__":
    api = SwanInference()
    api.inference(predict,
                  inputs=['list'],
                  outputs=['dict'],
                  description="a simple test")
    api.launch()

    demo = gr.Interface()
